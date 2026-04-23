"""
Agent 6 — Change Propagation

Triggers when source_of_truth_version in decisions.json exceeds the version
recorded in artifact_versions.json at the time of last generation.

Does NOT regenerate anything automatically. Outputs a change report with
recommended regeneration order and waits for human action.

Usage:
  python3 agents/change_propagation.py --project projects/<client>
  python3 agents/change_propagation.py --project projects/<client> --report-only
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from agents.utils.artifact_versions import load as load_artifact_versions, ARTIFACTS
from agents.utils.config import load_config

ARTIFACT_REGEN_COMMANDS = {
    "build_spec":   "python3 orchestrate.py generate --project {project_dir}",
    "figma_pngs":   "python3 orchestrate.py push    --project {project_dir}",
    "presentation": "node generate_presentation.js  --project {project_dir}",
}

ARTIFACT_DEPENDS_ON = {
    "figma_pngs":   "build_spec",
    "presentation": "figma_pngs",
}


def _load_decisions(project_dir: Path) -> dict:
    d_path = project_dir / "decisions.json"
    if not d_path.exists():
        return {"source_of_truth_version": 0, "decisions": []}
    with open(d_path) as f:
        return json.load(f)


def _active_at_version(decisions: list, version: int) -> list:
    """
    Returns decisions that were active at the given version.
    A decision was active at version V if:
    - It was added at or before V (we approximate: all decisions with date_stamp present)
    - It had not yet been superseded (superseded_by is None or the superseding
      decision was added after that version — we can't track this precisely without
      per-decision version stamps, so we include all that are currently active)
    This is a best-effort approximation; the report flags additive vs. contradictory.
    """
    return [d for d in decisions if d.get("superseded_by") is None]


def _classify_change(decision: dict, stale_decisions: list) -> str:
    """Classify a decision change as ADDITIVE or CONTRADICTORY relative to stale state."""
    for old in stale_decisions:
        if old["id"] == decision.get("id"):
            return "UPDATED"
    supersedes = decision.get("supersedes", [])
    if supersedes:
        return "CONTRADICTORY"
    return "ADDITIVE"


def detect_and_report(project_dir: str, report_only: bool = False) -> bool:
    """
    Returns True if any artifact is stale (drift detected), False if all are current.
    """
    project_path = Path(project_dir)
    config = load_config(project_dir)
    client_name = config.get("client_name", project_path.name)

    decisions_data = _load_decisions(project_path)
    current_version = decisions_data.get("source_of_truth_version", 0)
    all_decisions = decisions_data.get("decisions", [])
    active_decisions = _active_at_version(all_decisions, current_version)

    av = load_artifact_versions(project_dir)

    if current_version == 0:
        print("No decisions ingested yet (source_of_truth_version is 0). Nothing to check.")
        return False

    # Check which artifacts are stale
    stale = []
    for artifact in ARTIFACTS:
        entry = av.get(artifact)
        if not entry:
            stale.append((artifact, 0))
        elif entry["source_of_truth_version"] < current_version:
            stale.append((artifact, entry["source_of_truth_version"]))

    if not stale:
        print(f"All artifacts are current at v{current_version}. No drift detected.")
        return False

    # Build report
    now = datetime.now(timezone.utc).isoformat()
    lines = []
    lines.append(f"Change Report — {client_name}")
    lines.append(f"Generated: {now}")
    lines.append(f"Source of truth: v{current_version}")
    lines.append("━" * 60)
    lines.append("")

    regen_order = []

    for artifact, artifact_version in stale:
        entry = av.get(artifact, {})
        built_at = entry.get("generated_at", "never")
        lines.append(f"STALE: {artifact} (built at v{artifact_version}, current: v{current_version})")

        # Dependency note
        dep = ARTIFACT_DEPENDS_ON.get(artifact)
        if dep and any(a == dep for a, _ in stale):
            lines.append(f"  Dependency: {dep} must be regenerated first.")

        # Changed decisions since artifact_version
        changed = [
            d for d in active_decisions
            if d not in _active_at_version(all_decisions, artifact_version)
        ]
        # Fallback: show all decisions superseded after artifact_version
        superseded_since = [
            d for d in all_decisions
            if d.get("superseded_by") is not None
        ]

        new_since = [
            d for d in all_decisions
            if d.get("superseded_by") is None
            and d not in _active_at_version(all_decisions, artifact_version)
        ]

        if new_since or superseded_since:
            lines.append("  Decisions changed since last generation:")
            for d in new_since[:20]:
                change_type = _classify_change(d, [])
                supersedes_str = ""
                if d.get("supersedes"):
                    supersedes_str = f"  Supersedes: {', '.join(d['supersedes'])}"
                lines.append(f"    [+] {d['id']}  \"{d['decision'][:70]}\"")
                lines.append(f"         Tags: {', '.join(d.get('tags', []))}")
                lines.append(f"         Type: {change_type}")
                if supersedes_str:
                    lines.append(f"         {supersedes_str}")
            for d in superseded_since[:10]:
                lines.append(f"    [-] {d['id']}  \"{d['decision'][:70]}\"  (archived)")
        else:
            lines.append("  (Version mismatch but no specific changed decisions identified)")

        lines.append("")
        regen_order.append(artifact)

    lines.append("━" * 60)
    lines.append("Recommended regeneration order:")
    for i, artifact in enumerate(regen_order, 1):
        cmd = ARTIFACT_REGEN_COMMANDS.get(artifact, "").format(project_dir=project_dir)
        lines.append(f"  {i}. {artifact}  →  {cmd}")

    lines.append("")
    lines.append("Human review required. No regeneration has been performed.")

    report_text = "\n".join(lines)

    # Print to console
    print("\n" + report_text)

    # Write report file
    report_filename = f"change_report_v{current_version}.md"
    report_path = project_path / report_filename
    with open(report_path, "w") as f:
        f.write(report_text)
    print(f"\nReport saved: {report_path}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SF UX Orchestrator — Change Propagation Agent")
    parser.add_argument("--project", required=True, help="Path to project directory")
    parser.add_argument("--report-only", action="store_true",
                        help="Print report without prompting (non-interactive mode)")
    args = parser.parse_args()
    has_drift = detect_and_report(args.project, report_only=args.report_only)
    sys.exit(1 if has_drift else 0)
