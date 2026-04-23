"""
SF UX Orchestrator — main entry point.

Usage:
  python orchestrate.py generate --project projects/<client> [--channels web]
  python orchestrate.py push     --project projects/<client> [--port 7070] [--timeout 300]
  python orchestrate.py export   --project projects/<client>
  python orchestrate.py run      --project projects/<client>   # generate + push + export
"""
import argparse
from pathlib import Path

from integrations.figma.screen_generator import generate_screens
from integrations.figma.exporter import export_screens


def cmd_generate(project_dir: str, channels: list = None, screens: int = 1):
    manifest_path = str(Path(project_dir) / "manifest.json")
    print(f"Generating screens from {manifest_path}...")
    generate_screens(manifest_path, project_dir, only_channels=channels, max_screens=screens)


def cmd_push(project_dir: str, port: int = 7070, timeout: int = 300):
    from integrations.figma.plugin_builder import build_plugin
    from integrations.figma.plugin_server import PluginServer
    from integrations.figma.file_manager import load_project

    pending_dir = Path("exports/pending")
    plugin_dir = Path("exports/plugin")

    pending = list(pending_dir.glob("*.json"))
    if not pending:
        print("No pending frames found. Run 'generate' first.")
        return

    print(f"Found {len(pending)} pending frame(s).")

    server_url = f"http://localhost:{port}"
    build_plugin(plugin_dir, server_url=server_url)
    print(f"Plugin written to {plugin_dir.resolve()}/")

    project = load_project(project_dir)
    file_url = project["figma"].get("file_url", "(see project.json)")

    print()
    print("=" * 62)
    print("  ONE-TIME STEP: run the plugin in Figma desktop")
    print("=" * 62)
    print(f"  1. Open: {file_url}")
    print(f"  2. Plugins → Development → Import plugin from manifest")
    print(f"     Select: {(plugin_dir / 'manifest.json').resolve()}")
    print(f"  3. Plugins → Development → SF UX Orchestrator  → Run")
    print("=" * 62)
    print(f"  Waiting up to {timeout}s for plugin to complete...")
    print()

    server = PluginServer(pending_dir, project_dir, port=port, timeout=timeout)
    success = server.start()

    if success:
        print(f"Handoff complete. project.json updated with real Figma IDs.")
    else:
        print(f"Timeout reached ({timeout}s). Run 'push' again after running the plugin in Figma.")


def cmd_export(project_dir: str):
    print(f"Exporting screens from {project_dir}...")
    export_screens(project_dir)


def main():
    parser = argparse.ArgumentParser(description="SF UX Orchestrator")
    parser.add_argument("command", choices=["generate", "push", "export", "run"])
    parser.add_argument("--project", required=True,
                        help="Path to project directory (contains manifest.json + project.json)")
    parser.add_argument("--channels", nargs="+", choices=["web", "sms", "email"],
                        help="Restrict output to specific channels (e.g. --channels web)")
    parser.add_argument("--screens", type=int, default=1,
                        help="Number of screens (steps) to generate per flow (default: 1)")
    parser.add_argument("--port", type=int, default=7070,
                        help="Local server port for plugin handoff (default: 7070)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Seconds to wait for plugin to complete (default: 300)")
    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.project, channels=args.channels, screens=args.screens)
    elif args.command == "push":
        cmd_push(args.project, port=args.port, timeout=args.timeout)
    elif args.command == "export":
        cmd_export(args.project)
    elif args.command == "run":
        cmd_generate(args.project, channels=args.channels, screens=args.screens)
        cmd_push(args.project, port=args.port, timeout=args.timeout)
        cmd_export(args.project)


if __name__ == "__main__":
    main()
