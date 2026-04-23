"""
Local HTTP server that bridges Python-generated frame payloads to the Figma Plugin.

GET  /frames   → returns all pending frame JSON payloads as an array
POST /complete → receives [{name, id}] from plugin, updates project.json, shuts down
"""
import http.server
import json
import sys
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from integrations.figma.file_manager import load_project, save_project

PORT = 7070
TIMEOUT_SECONDS = 300


class PluginServer:
    def __init__(self, pending_dir: Path, project_dir: str,
                 port: int = PORT, timeout: int = TIMEOUT_SECONDS):
        self.pending_dir = Path(pending_dir)
        self.project_dir = project_dir
        self.port = port
        self.timeout = timeout
        self.shutdown_event = threading.Event()
        self.httpd = None

    def start(self) -> bool:
        """
        Starts the HTTP server in a daemon thread and blocks the main thread
        until the plugin calls POST /complete or the timeout expires.
        Returns True on success, False on timeout.
        """
        try:
            handler_class = self._make_handler()
            self.httpd = http.server.HTTPServer(("localhost", self.port), handler_class)
        except OSError as e:
            raise RuntimeError(
                f"Port {self.port} is already in use. "
                f"Stop the conflicting process or pass --port XXXX."
            ) from e

        server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        server_thread.start()

        completed = self.shutdown_event.wait(timeout=self.timeout)
        self.httpd.shutdown()
        server_thread.join(timeout=5)
        return completed

    def _make_handler(self):
        server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass  # suppress default request logging

            def _send_cors_headers(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def do_OPTIONS(self):
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()

            def do_GET(self):
                if self.path == "/frames":
                    server._handle_get_frames(self)
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == "/complete":
                    server._handle_post_complete(self)
                else:
                    self.send_response(404)
                    self.end_headers()

        return Handler

    def _handle_get_frames(self, handler):
        payloads = []
        for path in sorted(self.pending_dir.glob("*.json")):
            with open(path) as f:
                payloads.append(json.load(f))

        body = json.dumps(payloads).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler._send_cors_headers()
        handler.end_headers()
        handler.wfile.write(body)

    def _handle_post_complete(self, handler):
        length = int(handler.headers.get("Content-Length", 0))
        body = handler.rfile.read(length)
        results = json.loads(body)

        self._update_project_json(results)

        resp = json.dumps({"ok": True}).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(resp)))
        handler._send_cors_headers()
        handler.end_headers()
        handler.wfile.write(resp)

        self.shutdown_event.set()

    def _update_project_json(self, results: list):
        project = load_project(self.project_dir)
        name_to_id = {r["name"]: r["id"] for r in results}

        for frame in project["figma"]["generated_frames"]:
            real_id = name_to_id.get(frame["frame_name"])
            if real_id:
                frame["frame_id"] = real_id

        save_project(self.project_dir, project)

        ack_dir = Path("exports/acknowledged")
        ack_dir.mkdir(parents=True, exist_ok=True)
        for result in results:
            # frame_name uses / separators; safe filename uses _
            safe = result["name"].replace("/", "_").replace(" ", "-")
            src = self.pending_dir / f"{safe}.json"
            if src.exists():
                src.rename(ack_dir / f"{safe}.json")

        # Record figma_pngs artifact version
        try:
            from agents.utils.artifact_versions import record, decisions_version
            version = decisions_version(self.project_dir)
            export_path = project.get("export", {}).get("export_path", "exports/screens")
            record(self.project_dir, "figma_pngs", version, export_path)
        except Exception:
            pass
