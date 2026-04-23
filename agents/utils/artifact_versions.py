"""
Reads and writes artifact_versions.json in a project directory.
Tracks the source_of_truth_version at the time each artifact was last generated.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ARTIFACTS = ("build_spec", "figma_pngs", "presentation")


def load(project_dir: str) -> dict:
    path = Path(project_dir) / "artifact_versions.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def record(project_dir: str, artifact: str, source_of_truth_version: int, artifact_path: str) -> None:
    """Mark an artifact as freshly generated at the given decisions version."""
    data = load(project_dir)
    data[artifact] = {
        "source_of_truth_version": source_of_truth_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path": artifact_path,
    }
    out = Path(project_dir) / "artifact_versions.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)


def is_stale(project_dir: str, artifact: str, current_version: int) -> bool:
    """True if the artifact was generated at an older decisions version."""
    data = load(project_dir)
    entry = data.get(artifact)
    if not entry:
        return True
    return entry["source_of_truth_version"] < current_version


def decisions_version(project_dir: str) -> int:
    """Read current source_of_truth_version from decisions.json, or 0 if absent."""
    d_path = Path(project_dir) / "decisions.json"
    if not d_path.exists():
        return 0
    with open(d_path) as f:
        return json.load(f).get("source_of_truth_version", 0)
