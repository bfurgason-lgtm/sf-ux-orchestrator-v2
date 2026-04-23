"""
Exports generated Figma frames as @2x PNGs.
Frames are pulled by node ID from project.json and downloaded locally.
Output goes to the path defined in project.json → export.export_path.
"""
import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

from integrations.figma.file_manager import (
    load_project, save_project, _headers, FIGMA_API,
)

load_dotenv()


def export_screens(project_dir: str, flow_topic: str = None,
                   step_number: int = None, channel: str = None):
    """
    Exports frames from Figma at 2x scale as PNG.

    Filters:
    - flow_topic:   export only frames for this flow (None = all flows)
    - step_number:  export only this step (None = all steps)
    - channel:      export only this channel (None = all channels)
    """
    project = load_project(project_dir)
    file_key = project["figma"]["file_key"]
    scale = project["export"].get("scale", 2)
    fmt = project["export"].get("format", "PNG")
    out_path = Path(project["export"]["export_path"])
    out_path.mkdir(parents=True, exist_ok=True)

    frames = project["figma"]["generated_frames"]

    # Filter to frames that are not pending
    target_frames = [
        f for f in frames
        if not f["frame_id"].startswith("pending:")
        and (flow_topic is None or f["flow_topic"] == flow_topic)
        and (step_number is None or f["step_number"] == step_number)
        and (channel is None or f["channel"] == channel)
    ]

    if not target_frames:
        print("No exportable frames found (check for 'pending:' frame IDs).")
        return []

    node_ids = ",".join(f["frame_id"] for f in target_frames)

    print(f"Requesting {len(target_frames)} exports at {scale}x...")
    resp = requests.get(
        f"{FIGMA_API}/images/{file_key}",
        headers=_headers(),
        params={"ids": node_ids, "scale": scale, "format": fmt.lower()}
    )

    if resp.status_code != 200:
        print(f"Export request failed ({resp.status_code}): {resp.text[:300]}")
        return []

    image_map = resp.json().get("images", {})
    downloaded = []

    for frame in target_frames:
        fid = frame["frame_id"]
        url = image_map.get(fid)
        if not url:
            print(f"  No URL returned for {frame['frame_name']}")
            continue

        safe_name = frame["frame_name"].replace("/", "_").replace(" ", "-")
        file_path = out_path / f"{safe_name}@{scale}x.{fmt.lower()}"

        img_resp = requests.get(url)
        if img_resp.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(img_resp.content)
            downloaded.append(str(file_path))
            print(f"  Saved: {file_path}")
        else:
            print(f"  Download failed for {frame['frame_name']}: {img_resp.status_code}")

    project["export"]["last_export_at"] = datetime.now(timezone.utc).isoformat()
    save_project(project_dir, project)

    print(f"\nExported {len(downloaded)} of {len(target_frames)} frames to {out_path}")
    return downloaded
