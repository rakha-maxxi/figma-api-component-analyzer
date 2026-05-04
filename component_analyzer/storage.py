"""Simple JSON-backed analysis storage."""

import json
import threading
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ANALYSIS_FILE = DATA_DIR / "analyses.json"


class AnalysisStore:
    def __init__(self):
        self._lock = threading.Lock()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not ANALYSIS_FILE.exists():
            ANALYSIS_FILE.write_text("[]", encoding="utf-8")

    def list(self):
        with self._lock:
            items = self._load()
        return [
            {
                "id": item["id"],
                "file_name": item["meta"]["file_name"],
                "project_name": item["meta"]["project_name"],
                "platform": item["meta"]["platform"],
                "analyzed_at": item["meta"]["analyzed_at"],
                "source": item["meta"]["source"],
                "summary": item["summary"],
            }
            for item in items
        ]

    def get(self, analysis_id):
        with self._lock:
            items = self._load()
        for item in items:
            if item["id"] == analysis_id:
                return item
        return None

    def save(self, analysis):
        with self._lock:
            items = self._load()
            items = [item for item in items if item["id"] != analysis["id"]]
            items.insert(0, analysis)
            ANALYSIS_FILE.write_text(json.dumps(items[:40], indent=2), encoding="utf-8")

    def _load(self):
        return json.loads(ANALYSIS_FILE.read_text(encoding="utf-8"))
