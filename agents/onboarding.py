"""
Agent 1 — Onboarding

Entry point: run interactively from the repo root.
  python3 agents/onboarding.py

Or point at an existing project to resume onboarding:
  python3 agents/onboarding.py --project projects/<client>

Six-turn dialogue, one question at a time. Each answer is written to
config.user.json before the next question is asked. Partial completion
is safe — the user is never blocked from running downstream agents with
whatever is already configured.

Turn unlock sequence:
  1. Org/client name        → creates projects/{client}/ folder + all stubs
  2. Channels in scope      → activates channel config
  3. Order lookup field     → unlocks order confirmation step
  4. Status values          → unlocks status tracking step
  5. Unmatched order state  → unlocks edge case slides
  6. Additional edge cases  → adds to edge case queue
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from agents.utils.config import load_config, save_user_config

VALID_CHANNELS = {"web", "sms", "email"}

# Minimal project.json stub written on first run
_PROJECT_JSON_STUB = {
    "schema_version": "1.0",
    "figma": {
        "file_key": "",
        "file_name": "",
        "file_url": "",
        "last_frame_y": 0,
        "frame_gap": 80,
        "generated_frames": [],
        "last_frame_x": 0,
    },
    "channels": [],
    "branding": {
        "enabled": False,
        "persona_name": None,
        "persona_avatar_url": None,
        "primary_color": None,
        "secondary_color": None,
        "font_family": None,
    },
    "slds": {
        "components_file_key": "",
        "agentic_file_key": "",
        "validation_enabled": False,
    },
    "export": {
        "scale": 2,
        "format": "PNG",
        "last_export_at": None,
        "export_path": "",
    },
}

# Minimal manifest.json stub
_MANIFEST_STUB = {
    "schema_version": "0.5",
    "initiative_metadata": {
        "name": "",
        "version": "1.0",
        "timestamp": "",
        "brand_context": {
            "primary_brand": "",
            "sub_brands": [],
            "brand_guidelines_url": None,
        },
        "handoff_metadata": {
            "last_updated_by": "onboarding-agent",
            "last_updated_at": "",
            "status": "active",
            "handoff_notes": "Created by onboarding agent",
            "design_review_status": "pending",
        },
    },
    "data_tier": "2",
    "design_system": {
        "framework": "slds_v2",
        "theme": "light",
        "brand_tokens": {
            "primary_color": "#0070D2",
            "secondary_color": "#5C6B73",
            "accent_color": "#45C65A",
            "font_family": "Salesforce Sans",
        },
        "accessibility": {
            "wcag_level": "AA",
            "color_contrast_verified": False,
            "screen_reader_optimized": True,
        },
        "responsive_breakpoints": {
            "mobile": "390px",
            "tablet": "768px",
            "desktop": "1200px",
        },
    },
    "flows": [],
    "terminology_map": {},
    "drive": {
        "project_folder": "",
        "exports_folder": "",
        "auto_sync": False,
    },
    "figma": {
        "target_file_url": None,
        "design_system_library": None,
        "brand_kit_library": None,
    },
    "deployment": {
        "target_org": None,
        "release_date": None,
        "stakeholder_reviews": [],
    },
}

# Minimal decisions.json stub
_DECISIONS_STUB = {
    "source_of_truth_version": 0,
    "last_run_at": None,
    "decisions": [],
}

# artifact_versions stub
_ARTIFACT_VERSIONS_STUB = {}


def _ask(prompt: str, *, default: str = None) -> str:
    display = f"{prompt}"
    if default:
        display += f" [{default}]"
    display += "\n> "
    try:
        answer = input(display).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return answer if answer else (default or "")


def _client_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))


def _create_project_folder(client_name: str) -> Path:
    slug = _client_slug(client_name)
    project_dir = _REPO_ROOT / "projects" / slug
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "transcripts").mkdir(exist_ok=True)
    return project_dir


def _write_stub(project_dir: Path, filename: str, data: dict) -> None:
    path = project_dir / filename
    if not path.exists():
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def _update_manifest_meta(project_dir: Path, client_name: str, channels: list) -> None:
    manifest_path = project_dir / "manifest.json"
    if not manifest_path.exists():
        return
    with open(manifest_path) as f:
        manifest = json.load(f)
    now = datetime.now(timezone.utc).isoformat()
    manifest["initiative_metadata"]["name"] = f"{client_name} Agentforce"
    manifest["initiative_metadata"]["brand_context"]["primary_brand"] = client_name
    manifest["initiative_metadata"]["timestamp"] = now
    manifest["initiative_metadata"]["handoff_metadata"]["last_updated_at"] = now
    manifest["drive"]["project_folder"] = str(project_dir)
    manifest["drive"]["exports_folder"] = str(_REPO_ROOT / "exports" / _client_slug(client_name))
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def _update_project_json(project_dir: Path, client_name: str, channels: list) -> None:
    project_path = project_dir / "project.json"
    if not project_path.exists():
        return
    with open(project_path) as f:
        project = json.load(f)
    slug = _client_slug(client_name)
    project["channels"] = channels
    project["figma"]["file_name"] = f"{client_name} — Agentforce Flows"
    project["export"]["export_path"] = f"exports/{slug}/screens"
    project["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(project_path, "w") as f:
        json.dump(project, f, indent=2)


def run_onboarding(project_dir_arg: str = None):
    print("\n── SF UX Orchestrator — Onboarding ──────────────────────────────────")
    print("One question at a time. Press Enter to accept the default.")
    print("You can re-run this script any time to update answers.\n")

    # ── Turn 1: Client name ───────────────────────────────────────────────────
    if project_dir_arg:
        project_dir = Path(project_dir_arg)
        if not project_dir.is_absolute():
            project_dir = _REPO_ROOT / project_dir
        existing_config = load_config(str(project_dir))
        default_name = existing_config.get("client_name", "")
        if default_name == "Unnamed Client":
            default_name = ""
    else:
        default_name = ""

    client_name = _ask("1/6  What is your org or client name?", default=default_name or None)
    if not client_name:
        print("Client name is required.")
        sys.exit(1)

    project_dir = _create_project_folder(client_name)
    slug = _client_slug(client_name)

    # Write all stubs (skip if already exist)
    _write_stub(project_dir, "manifest.json", _MANIFEST_STUB)
    _write_stub(project_dir, "decisions.json", _DECISIONS_STUB)
    _write_stub(project_dir, "artifact_versions.json", _ARTIFACT_VERSIONS_STUB)

    project_stub = {
        **_PROJECT_JSON_STUB,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_stub(project_dir, "project.json", project_stub)

    save_user_config(str(project_dir), {
        "client_name": client_name,
        "exports_slug": slug,
    })
    _update_manifest_meta(project_dir, client_name, [])
    print(f"  ✓ Project folder: projects/{slug}/\n")

    # ── Turn 2: Channels ──────────────────────────────────────────────────────
    raw_channels = _ask(
        "2/6  Which channels are in scope? (web / sms / email — comma-separated)",
        default="web",
    )
    channels = [c.strip().lower() for c in raw_channels.replace("/", ",").split(",")]
    channels = [c for c in channels if c in VALID_CHANNELS]
    if not channels:
        channels = ["web"]

    save_user_config(str(project_dir), {"channels": channels})
    _update_project_json(project_dir, client_name, channels)
    print(f"  ✓ Channels: {', '.join(channels)}\n")

    # ── Turn 3: Order lookup field ────────────────────────────────────────────
    lookup_field = _ask(
        "3/6  What Salesforce field is used to look up a customer's order?\n"
        "     (e.g. Order_Number__c, OrderNumber)",
        default="OrderNumber",
    )
    save_user_config(str(project_dir), {"order_lookup_field": lookup_field})
    print(f"  ✓ Order lookup field: {lookup_field}\n")

    # ── Turn 4: Status values ─────────────────────────────────────────────────
    raw_statuses = _ask(
        "4/6  What order status values does your system use?\n"
        "     (comma-separated, e.g. In Transit, Delivered, Pending)",
        default="In Transit, Delivered, Pending",
    )
    status_values = [s.strip() for s in raw_statuses.split(",") if s.strip()]
    save_user_config(str(project_dir), {"status_values": status_values})
    print(f"  ✓ Status values: {', '.join(status_values)}\n")

    # ── Turn 5: Unmatched order state ─────────────────────────────────────────
    unmatched = _ask(
        "5/6  What happens when an order can't be found?\n"
        "     Describe the fallback, or press Enter for the default.",
        default="Show empathetic error message with alternative lookup options",
    )
    save_user_config(str(project_dir), {"unmatched_order_state": unmatched})
    print(f"  ✓ Unmatched order state saved.\n")

    # ── Turn 6: Additional edge cases ─────────────────────────────────────────
    raw_edges = _ask(
        "6/6  Any additional edge cases to document?\n"
        "     (comma-separated names, or press Enter to skip)",
        default="",
    )
    edge_cases = [e.strip() for e in raw_edges.split(",") if e.strip()] if raw_edges else []
    save_user_config(str(project_dir), {"edge_cases": edge_cases})
    if edge_cases:
        print(f"  ✓ Edge cases queued: {', '.join(edge_cases)}\n")
    else:
        print("  ✓ No additional edge cases.\n")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("── Onboarding complete ──────────────────────────────────────────────")
    print(f"  Project:  projects/{slug}/")
    print(f"  Channels: {', '.join(channels)}")
    print(f"  Config:   projects/{slug}/config.user.json")
    print()
    print("Next steps:")
    print(f"  • Drop transcripts into projects/{slug}/transcripts/")
    print(f"    Then run: python3 agents/ingestion.py --project projects/{slug}")
    print(f"  • Or run the full pipeline:")
    print(f"    python3 orchestrate.py run --project projects/{slug}")
    print()

    return str(project_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SF UX Orchestrator — Onboarding Agent")
    parser.add_argument("--project", help="Existing project dir to resume onboarding")
    args = parser.parse_args()
    run_onboarding(args.project)
