"""
Config loader used by all agents.
Merges core/config.defaults.json with projects/{client}/config.user.json.
User values always win; defaults fill gaps.
"""
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_DEFAULTS_PATH = _REPO_ROOT / "core" / "config.defaults.json"


def load_config(project_dir: str) -> dict:
    with open(_DEFAULTS_PATH) as f:
        defaults = json.load(f)

    user_path = Path(project_dir) / "config.user.json"
    if user_path.exists():
        with open(user_path) as f:
            user = json.load(f)
    else:
        user = {}

    return {**defaults, **user}


def save_user_config(project_dir: str, updates: dict) -> None:
    user_path = Path(project_dir) / "config.user.json"
    existing = {}
    if user_path.exists():
        with open(user_path) as f:
            existing = json.load(f)
    existing.update(updates)
    with open(user_path, "w") as f:
        json.dump(existing, f, indent=2)
