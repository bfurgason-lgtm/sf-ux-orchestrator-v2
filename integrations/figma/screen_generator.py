"""
Screen generator: reads manifest.json steps and writes one Figma frame
per step per channel.

Each frame payload is a flat structure the plugin consumes:
  - chat channels (web/sms): { frame_name, channel, frame_width, frame_height,
                               x, y, messages: [{role, text}] }
  - email channel:            { frame_name, channel, frame_width, frame_height,
                               x, y, subject, body }

The plugin uses figma.importComponentByKeyAsync() with real SLDS Agentic
Experiences components — no raw shape drawing.
"""

import json
from pathlib import Path

import requests
from dotenv import load_dotenv

from integrations.figma.file_manager import (
    ensure_file, record_frame, already_generated,
    next_col_x, channel_y_offset,
    CHANNEL_WIDTHS, CHANNEL_HEIGHTS, _headers, FIGMA_API,
)

load_dotenv()


def _messages_for_steps(steps: list, channel: str) -> list:
    """
    Builds a flat [{role, text}] message list from all steps up to and
    including the current step (cumulative conversation thread).
    """
    messages = []
    for step in steps:
        ch = step.get("channels", {}).get(channel, {})
        agent = ch.get("agent", step.get("utterances", {}).get("agent", ""))
        user  = ch.get("user",  step.get("utterances", {}).get("user",  ""))
        if agent:
            messages.append({"role": "agent", "text": agent})
        if user:
            messages.append({"role": "user",  "text": user})
    return messages


def build_chat_payload(flow_topic: str, step_number: int,
                       channel: str, all_steps_so_far: list,
                       x: float, y: float,
                       agent_name: str = "Agent",
                       quick_replies: list = None) -> dict:
    w = CHANNEL_WIDTHS[channel]
    h = CHANNEL_HEIGHTS[channel]
    payload = {
        "frame_name":   f"{flow_topic}/step-{step_number}/{channel}",
        "channel":      channel,
        "frame_width":  w,
        "frame_height": h,
        "x": x,
        "y": y,
        "messages": _messages_for_steps(all_steps_so_far, channel),
        "agent_name": agent_name,
    }
    if quick_replies:
        payload["quick_replies"] = quick_replies
    return payload


def build_email_payload(flow_topic: str, step_number: int,
                        step: dict, x: float, y: float) -> dict:
    w = CHANNEL_WIDTHS["email"]
    h = CHANNEL_HEIGHTS["email"]
    ch = step.get("channels", {}).get("email", {})
    return {
        "frame_name":   f"{flow_topic}/step-{step_number}/email",
        "channel":      "email",
        "frame_width":  w,
        "frame_height": h,
        "x": x,
        "y": y,
        "subject": ch.get("subject", f"Step {step_number}"),
        "body":    ch.get("body", step.get("utterances", {}).get("agent", "")),
    }


def generate_screens(manifest_path: str, project_dir: str,
                     only_channels: list = None, max_screens: int = None):
    with open(manifest_path) as f:
        manifest = json.load(f)

    project  = ensure_file(project_dir)
    channels = only_channels or project["channels"]
    branding = project["branding"]

    meta       = manifest.get("initiative_metadata", {})
    brand      = meta.get("brand_context", {})
    agent_name = brand.get("primary_brand") or meta.get("name") or "Agent"

    for flow in manifest.get("flows", []):
        topic      = flow["topic"]
        steps      = flow["steps"]
        f_channels = flow.get("channels", channels)

        for i, step in enumerate(steps[:max_screens] if max_screens else steps):
            step_num     = step["step_number"]
            steps_so_far = steps[:i + 1]
            x_col        = next_col_x(project)

            for channel in channels:
                if channel not in f_channels:
                    continue
                if already_generated(project, topic, step_num, channel):
                    print(f"  Skip (exists): {topic}/step-{step_num}/{channel}")
                    continue

                y = channel_y_offset(channels, channel, active_channels=only_channels)

                if channel == "email":
                    payload = build_email_payload(topic, step_num, step, x_col, y)
                else:
                    sms_ch       = step.get("channels", {}).get("sms", {})
                    quick_replies = sms_ch.get("quick_replies") if channel == "sms" else None
                    payload = build_chat_payload(topic, step_num, channel,
                                                 steps_so_far, x_col, y,
                                                 agent_name=agent_name,
                                                 quick_replies=quick_replies)

                result = _write_frame(project["figma"]["file_key"], payload)
                if result:
                    record_frame(project_dir, project, topic, step_num,
                                 channel, result, payload["frame_name"], x_col, y)
                    print(f"  Created: {payload['frame_name']} at ({x_col}, {y})")
                else:
                    print(f"  Failed:  {payload['frame_name']}")

            project = _reload_project(project_dir)

    _save_build_spec(project_dir, manifest)
    print(f"\nDone. View file: {project['figma']['file_url']}")


def _write_frame(file_key: str, payload: dict) -> str | None:
    """
    Tries the Figma Write API; falls back to saving a pending JSON for plugin pickup.
    Returns the frame ID (real or "pending:<name>").
    """
    resp = requests.post(
        f"{FIGMA_API}/files/{file_key}/nodes",
        headers={**_headers(), "Content-Type": "application/json"},
        json={"nodes": [payload]},
    )
    if resp.status_code == 200:
        created = resp.json().get("nodes", [])
        return created[0].get("id") if created else None

    _save_pending(payload)
    return f"pending:{payload['frame_name']}"


def _save_pending(payload: dict):
    out_dir = Path("exports/pending")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = payload["frame_name"].replace("/", "_").replace(" ", "-")
    with open(out_dir / f"{safe}.json", "w") as f:
        json.dump(payload, f, indent=2)


def _save_build_spec(project_dir: str, manifest: dict):
    """Writes a snapshot of the pending payloads + manifest to exports/build_spec.json."""
    pending_dir = Path("exports/pending")
    payloads = []
    for path in sorted(pending_dir.glob("*.json")):
        with open(path) as f:
            payloads.append(json.load(f))
    spec = {
        "manifest": manifest,
        "frame_payloads": payloads,
    }
    out = Path(project_dir) / "build_spec.json"
    with open(out, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"  Build spec saved: {out}")


def _reload_project(project_dir: str) -> dict:
    path = Path(project_dir) / "project.json"
    with open(path) as f:
        return json.load(f)
