"""Dependency-free HTTP server for the Figma component refactor analyzer."""

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import traceback

from .analyzer import analyze_figma_file
from .figma_client import FigmaApiError, fetch_file
from .storage import AnalysisStore


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STORE = AnalysisStore()
PROJECT_ROOT = BASE_DIR.parent


def load_local_env():
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and value and key not in os.environ:
            os.environ[key] = value


class AnalyzerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if path == "/assets/styles.css":
            self._serve_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
            return
        if path == "/assets/app.js":
            self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        if path == "/api/health":
            self._json({"ok": True})
            return
        if path == "/api/analyses":
            self._json({"items": STORE.list()})
            return
        if path.startswith("/api/analyses/"):
            analysis_id = path.rsplit("/", 1)[-1]
            analysis = STORE.get(analysis_id)
            if not analysis:
                self._json({"error": "Analysis not found."}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(analysis)
            return
        self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/api/analyze":
            self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            token = payload.get("token") or os.environ.get("FIGMA_TOKEN")
            file_key = (payload.get("file_key") or "").strip()
            reference_file_key = (payload.get("reference_file_key") or "").strip()
            enable_reference_compare = payload.get("enable_reference_compare") in {True, "true", "on", "1", 1}
            project_name = (payload.get("project_name") or "").strip() or "Unknown Project"
            platform = (payload.get("platform") or "").strip() or "Unknown Platform"

            file_data = fetch_file(file_key, token=token)
            reference_file_data = fetch_file(reference_file_key, token=token) if reference_file_key and enable_reference_compare else None
            analysis = analyze_figma_file(
                file_data,
                {
                    "file_key": file_key,
                    "reference_file_key": reference_file_key if enable_reference_compare else "",
                    "project_name": project_name,
                    "platform": platform,
                },
                reference_file_data=reference_file_data,
            )
            STORE.save(analysis)
            self._json(analysis, status=HTTPStatus.CREATED)
        except FigmaApiError as error:
            self._json({"error": str(error)}, status=HTTPStatus.BAD_GATEWAY)
        except ValueError as error:
            self._json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as error:  # pragma: no cover - defensive path
            traceback.print_exc()
            self._json({"error": f"Unexpected server error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format, *args):  # noqa: A003
        return

    def _serve_file(self, file_path, content_type):
        if not file_path.exists():
            self._json({"error": "Static asset not found."}, status=HTTPStatus.NOT_FOUND)
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("Request body is required.")
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("Request body must be valid JSON.") from error


def run(host="127.0.0.1", port=8123):
    load_local_env()
    server = ThreadingHTTPServer((host, port), AnalyzerHandler)
    print(f"MAI Component Analyzer running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
