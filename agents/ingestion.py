"""
Agent 2 — Ingestion

Watches projects/{client}/transcripts/ for .txt, .md, .pdf, .docx files.
Parses each file, extracts decisions, classifies conflicts via Claude API,
and writes decisions.json.

Usage:
  python3 agents/ingestion.py --project projects/<client>
  python3 agents/ingestion.py --project projects/<client> --detect   (drop-zone mode)

Conflict rule: more recent meeting_date wins. If dates are equal or absent,
newer date_stamp (ingestion order) wins. Old decisions are archived with
superseded_by set — never deleted.

After each run prints:
  - N new decisions added
  - N decisions superseded
  - Conflicts and how they were resolved
  - Current source_of_truth_version
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from agents.utils.config import load_config
from agents.utils.artifact_versions import decisions_version

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

VALID_TAGS = {"flow", "edge-case", "branding", "lookup-field", "status", "general"}


# ─── File readers ─────────────────────────────────────────────────────────────

def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        print(f"  [warn] pdfplumber not installed — skipping {path.name}. Run: pip install pdfplumber")
        return ""


def _read_docx(path: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        print(f"  [warn] python-docx not installed — skipping {path.name}. Run: pip install python-docx")
        return ""


def read_transcript(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".txt", ".md"):
        return _read_txt(path)
    elif ext == ".pdf":
        return _read_pdf(path)
    elif ext == ".docx":
        return _read_docx(path)
    return ""


# ─── Date extraction ──────────────────────────────────────────────────────────

_DATE_PATTERNS = [
    r"\b(\d{4}-\d{2}-\d{2})\b",
    r"\b(\w+ \d{1,2},\s*\d{4})\b",
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
    r"(?:Meeting|Date|Session)[:\s]+(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},?\s*\d{4})",
]

def _parse_meeting_date(text: str):
    for pattern in _DATE_PATTERNS:
        match = re.search(pattern, text[:2000], re.IGNORECASE)
        if match:
            raw = match.group(1)
            for fmt in ("%Y-%m-%d", "%B %d, %Y", "%B %d %Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
    return None


# ─── Decision ID ──────────────────────────────────────────────────────────────

def _decision_id(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:8]


# ─── Claude API helpers ───────────────────────────────────────────────────────

def _claude_client():
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return None


def _extract_decisions_via_claude(client, transcript_text: str, source_file: str) -> list[dict]:
    """
    Uses Claude to extract structured decisions from a transcript.
    Returns list of {decision, tags} dicts.
    Falls back to empty list on failure.
    """
    prompt = f"""You are analyzing a meeting transcript or design document to extract UX decisions.

Extract every concrete UX decision from the text below. A decision is a specific, actionable statement about how something should work (e.g. "Order lookup uses the Order_Number__c field", "SMS channel is out of scope for Phase 1").

For each decision:
- Write it as a clear, present-tense statement (not a question or observation)
- Assign 1–3 tags from this list: flow, edge-case, branding, lookup-field, status, general
- Do NOT include vague statements, open questions, or non-decisions

Return ONLY valid JSON — an array of objects with keys "decision" and "tags":
[
  {{"decision": "...", "tags": ["flow"]}},
  ...
]

If there are no extractable decisions, return an empty array: []

Transcript ({source_file}):
---
{transcript_text[:8000]}
---"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        return json.loads(raw)
    except Exception as e:
        print(f"  [warn] Claude extraction failed: {e}")
        return []


def _classify_conflicts_via_claude(client, existing: list[dict], new_decisions: list[dict]) -> list[dict]:
    """
    Uses Claude to identify which new decisions contradict or supersede existing ones.
    Returns list of {new_id, supersedes_id, reason} dicts.
    Falls back to [] (no conflicts detected) on failure.
    """
    if not existing or not new_decisions:
        return []

    existing_summary = json.dumps([
        {"id": d["id"], "decision": d["decision"], "meeting_date": d.get("meeting_date"), "tags": d.get("tags", [])}
        for d in existing if d.get("superseded_by") is None
    ], indent=2)

    new_summary = json.dumps([
        {"id": d["id"], "decision": d["decision"], "tags": d.get("tags", [])}
        for d in new_decisions
    ], indent=2)

    prompt = f"""You are analyzing UX decisions for conflicts.

Below are EXISTING active decisions and NEW decisions just extracted from a transcript.

Identify pairs where a new decision CONTRADICTS or SUPERSEDES an existing one — meaning they cannot both be true at the same time.

Do NOT flag:
- Decisions that are on different topics
- Additive decisions (new info that doesn't contradict old info)
- Decisions that are identical

Return ONLY valid JSON — an array of conflict objects:
[
  {{
    "new_id": "<8-char id of the new decision>",
    "supersedes_id": "<8-char id of the existing decision being superseded>",
    "reason": "one sentence explaining why"
  }}
]

If there are no conflicts, return: []

EXISTING ACTIVE DECISIONS:
{existing_summary}

NEW DECISIONS:
{new_summary}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        return json.loads(raw)
    except Exception as e:
        print(f"  [warn] Claude conflict classification failed: {e}")
        return []


# ─── Fallback: deterministic extraction ───────────────────────────────────────

def _extract_decisions_fallback(text: str) -> list[dict]:
    """
    Minimal fallback when Claude is unavailable.
    Splits on sentence boundaries and treats lines with decision-like keywords as decisions.
    Only extracts; no conflict detection (ambiguous conflicts flagged for review).
    """
    keywords = re.compile(
        r"\b(will|shall|must|should|use|set|the .+ is|agreed|decided|confirmed|"
        r"field is|lookup via|status values?|channel|out of scope|in scope)\b",
        re.IGNORECASE,
    )
    lines = [l.strip() for l in re.split(r"[.\n]", text) if len(l.strip()) > 20]
    decisions = []
    for line in lines:
        if keywords.search(line):
            decisions.append({"decision": line, "tags": ["general"]})
    return decisions[:30]  # cap at 30 to avoid noise


# ─── decisions.json I/O ───────────────────────────────────────────────────────

def _load_decisions(project_dir: Path) -> dict:
    path = project_dir / "decisions.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"source_of_truth_version": 0, "last_run_at": None, "decisions": []}


def _save_decisions(project_dir: Path, data: dict) -> None:
    path = project_dir / "decisions.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─── Main ingestion logic ─────────────────────────────────────────────────────

def ingest(project_dir: str) -> None:
    project_path = Path(project_dir)
    transcripts_dir = project_path / "transcripts"

    if not transcripts_dir.exists():
        print(f"No transcripts/ directory found in {project_dir}")
        return

    files = sorted(
        f for f in transcripts_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        print(f"No supported transcript files found in {transcripts_dir}")
        print(f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        return

    data = _load_decisions(project_path)
    existing_decisions = data["decisions"]

    claude = _claude_client()
    if claude:
        print("  Using Claude API for decision extraction and conflict detection.")
    else:
        print("  [warn] ANTHROPIC_API_KEY not set — using fallback extraction. Conflict detection disabled.")

    stats = {"added": 0, "superseded": 0, "conflicts": []}

    for transcript_file in files:
        print(f"\n  Processing: {transcript_file.name}")
        text = read_transcript(transcript_file)
        if not text.strip():
            print(f"    [skip] Empty or unreadable file.")
            continue

        meeting_date = _parse_meeting_date(text)
        if meeting_date:
            print(f"    Detected meeting date: {meeting_date}")

        # Extract decisions
        if claude:
            raw_decisions = _extract_decisions_via_claude(claude, text, transcript_file.name)
        else:
            raw_decisions = _extract_decisions_fallback(text)

        if not raw_decisions:
            print(f"    No decisions extracted.")
            continue

        now = datetime.now(timezone.utc).isoformat()

        # Build new decision records
        new_records = []
        for item in raw_decisions:
            decision_text = item.get("decision", "").strip()
            if not decision_text:
                continue
            tags = [t for t in item.get("tags", ["general"]) if t in VALID_TAGS]
            if not tags:
                tags = ["general"]
            did = _decision_id(decision_text)
            # Skip exact duplicates already in the store
            if any(d["id"] == did for d in existing_decisions):
                continue
            new_records.append({
                "id": did,
                "decision": decision_text,
                "source_file": transcript_file.name,
                "date_stamp": now,
                "meeting_date": meeting_date,
                "supersedes": [],
                "superseded_by": None,
                "tags": tags,
            })

        if not new_records:
            print(f"    All decisions already in store (no new additions).")
            continue

        # Detect conflicts
        if claude:
            conflicts = _classify_conflicts_via_claude(claude, existing_decisions, new_records)
        else:
            conflicts = []
            # Fallback: flag exact-substring matches for human review
            for new in new_records:
                for old in existing_decisions:
                    if old.get("superseded_by") is not None:
                        continue
                    if new["decision"].lower() in old["decision"].lower() or \
                       old["decision"].lower() in new["decision"].lower():
                        print(f"    [review] Possible duplicate (manual check needed):")
                        print(f"      Old: {old['decision'][:80]}")
                        print(f"      New: {new['decision'][:80]}")

        # Apply conflicts: newer wins if it has a later meeting_date, else by ingestion order
        conflict_map = {}  # new_id → (supersedes_id, reason)
        for conflict in conflicts:
            nid = conflict.get("new_id")
            sid = conflict.get("supersedes_id")
            reason = conflict.get("reason", "")
            if not nid or not sid:
                continue

            new_rec = next((r for r in new_records if r["id"] == nid), None)
            old_rec = next((d for d in existing_decisions if d["id"] == sid), None)
            if not new_rec or not old_rec:
                continue

            # Date comparison
            new_date = new_rec.get("meeting_date")
            old_date = old_rec.get("meeting_date")

            if new_date and old_date and old_date > new_date:
                # Old is more recent — new is superseded instead
                new_rec["superseded_by"] = sid
                print(f"    Conflict resolved: OLD wins (meeting date {old_date} > {new_date})")
                print(f"      New '{new_rec['decision'][:60]}...' superseded by existing.")
                stats["conflicts"].append({
                    "winner_id": sid, "loser_id": nid,
                    "reason": reason, "resolution": "old wins by meeting date",
                })
            else:
                # New wins (later date or dates absent → ingestion order wins)
                conflict_map[nid] = (sid, reason)
                new_rec["supersedes"] = [sid]

        # Archive superseded old decisions
        for nid, (sid, reason) in conflict_map.items():
            for d in existing_decisions:
                if d["id"] == sid and d.get("superseded_by") is None:
                    d["superseded_by"] = nid
                    stats["superseded"] += 1
                    new_rec = next((r for r in new_records if r["id"] == nid), None)
                    new_date = new_rec["meeting_date"] if new_rec else None
                    old_date = d.get("meeting_date")
                    resolution = "more recent meeting date wins" if (new_date and old_date) else "ingestion order wins"
                    stats["conflicts"].append({
                        "winner_id": nid,
                        "loser_id": sid,
                        "reason": reason,
                        "resolution": resolution,
                    })
                    print(f"    Conflict: '{d['decision'][:60]}...'")
                    print(f"      → superseded by new decision (id: {nid})")
                    print(f"      Reason: {reason}")

        # Add new records to store (including those marked superseded)
        added_count = sum(1 for r in new_records if r.get("superseded_by") is None)
        existing_decisions.extend(new_records)
        stats["added"] += added_count
        print(f"    Added {added_count} new decision(s) from {transcript_file.name}")

    # Only bump version if at least one new decision was added this run
    if stats["added"] > 0:
        data["source_of_truth_version"] += 1
    data["last_run_at"] = datetime.now(timezone.utc).isoformat()
    data["decisions"] = existing_decisions
    _save_decisions(project_path, data)

    # ── Summary ───────────────────────────────────────────────────────────────
    new_version = data["source_of_truth_version"]
    print(f"\n── Ingestion complete ───────────────────────────────────────────────")
    print(f"  {stats['added']} new decision(s) added")
    print(f"  {stats['superseded']} decision(s) superseded")
    if stats["conflicts"]:
        print(f"\n  Conflicts resolved:")
        for c in stats["conflicts"]:
            winner = next((d for d in existing_decisions if d["id"] == c["winner_id"]), {})
            loser  = next((d for d in existing_decisions if d["id"] == c["loser_id"]),  {})
            print(f"    {c['loser_id']}: \"{loser.get('decision','')[:60]}\"")
            print(f"    → superseded by {c['winner_id']}: \"{winner.get('decision','')[:60]}\"")
            print(f"       Resolution: {c['resolution']}")
    print(f"\n  Current source_of_truth_version: {new_version}")
    print(f"  decisions.json: {project_path / 'decisions.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SF UX Orchestrator — Ingestion Agent")
    parser.add_argument("--project", required=True, help="Path to project directory")
    parser.add_argument("--detect", action="store_true",
                        help="Drop-zone mode: run if new transcripts are present")
    args = parser.parse_args()
    ingest(args.project)
