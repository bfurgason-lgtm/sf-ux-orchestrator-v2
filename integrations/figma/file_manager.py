"""
Manages the generated Figma output file for a project.
First run: creates a new file and writes the key to project.json.
Subsequent runs: loads the existing file key and resumes.
"""
import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FIGMA_TOKEN = os.getenv("FIGMA_ACCESS_TOKEN")
FIGMA_API = "https://api.figma.com/v1"

CHANNEL_WIDTHS = {
    "web":   340,
    "sms":   390,
    "email": 710,
}
CHANNEL_HEIGHTS = {
    "web":   629,
    "sms":   844,
    "email": 280,
}
CHANNEL_GAP = 60   # vertical gap between channel rows
FRAME_COL_GAP = 60 # horizontal gap between step columns


def _headers():
    return {"X-Figma-Token": FIGMA_TOKEN}


def load_project(project_dir: str) -> dict:
    path = Path(project_dir) / "project.json"
    with open(path) as f:
        return json.load(f)


def save_project(project_dir: str, project: dict):
    path = Path(project_dir) / "project.json"
    project["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(path, "w") as f:
        json.dump(project, f, indent=2)


def ensure_file(project_dir: str) -> dict:
    """
    Returns the project dict with a valid figma.file_key.
    Creates a new Figma file if none exists yet.
    """
    project = load_project(project_dir)

    if project["figma"]["file_key"]:
        print(f"Using existing Figma file: {project['figma']['file_url']}")
        return project

    print("No Figma file found — creating new file...")
    file_key = _create_figma_file(project["figma"]["file_name"])
    file_url = f"https://www.figma.com/design/{file_key}/"

    project["figma"]["file_key"] = file_key
    project["figma"]["file_url"] = file_url
    project["figma"]["last_frame_y"] = 0
    project["figma"]["generated_frames"] = []

    save_project(project_dir, project)
    print(f"Created Figma file: {file_url}")
    return project


def _create_figma_file(name: str) -> str:
    """
    Creates a new Figma file via the REST API.
    Returns the file key.
    """
    # Figma doesn't have a direct "create blank file" REST endpoint —
    # we use the drafts endpoint to create a file in the user's drafts.
    resp = requests.post(
        f"{FIGMA_API}/files",
        headers={**_headers(), "Content-Type": "application/json"},
        json={"name": name}
    )

    if resp.status_code == 200:
        return resp.json()["key"]

    # Fallback: create via team project if drafts endpoint unavailable
    # (Figma API v1 file creation is only available on certain plans)
    raise RuntimeError(
        f"Could not create Figma file (status {resp.status_code}): {resp.text}\n"
        "You may need to create the file manually in Figma and paste the file key "
        "into projects/<project>/project.json → figma.file_key"
    )


def record_frame(project_dir: str, project: dict, flow_topic: str,
                 step_number: int, channel: str, frame_id: str,
                 frame_name: str, x_position: float, y_position: float):
    """Appends a generated frame to the project log and updates last_frame_x."""
    project["figma"]["generated_frames"].append({
        "flow_topic":  flow_topic,
        "step_number": step_number,
        "channel":     channel,
        "frame_id":    frame_id,
        "frame_name":  frame_name,
        "x_position":  x_position,
        "y_position":  y_position,
    })
    right = x_position + CHANNEL_WIDTHS.get(channel, 340)
    if right > project["figma"].get("last_frame_x", 0):
        project["figma"]["last_frame_x"] = right
    save_project(project_dir, project)


def already_generated(project: dict, flow_topic: str,
                      step_number: int, channel: str) -> bool:
    """Returns True if this step+channel combo was already written to Figma."""
    for frame in project["figma"]["generated_frames"]:
        if (frame["flow_topic"] == flow_topic
                and frame["step_number"] == step_number
                and frame["channel"] == channel):
            return True
    return False


def next_col_x(project: dict) -> float:
    """X position for the left edge of the next step column."""
    last_x = project["figma"].get("last_frame_x", 0)
    gap = project["figma"].get("frame_gap", FRAME_COL_GAP)
    return last_x + gap if last_x > 0 else 100


def channel_y_offset(channels: list, channel: str, active_channels: list = None) -> float:
    """Vertical Y position for a channel row, stacking only active channels."""
    ordered = [ch for ch in channels if active_channels is None or ch in active_channels]
    y = 100
    for ch in ordered:
        if ch == channel:
            return y
        y += CHANNEL_HEIGHTS.get(ch, 629) + CHANNEL_GAP
    return y
