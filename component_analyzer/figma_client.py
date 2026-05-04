"""Minimal Figma API client for file analysis."""

import json
import socket
import urllib.error
import urllib.parse
import urllib.request

from .demo_data import build_demo_file, build_demo_master_file


FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaApiError(Exception):
    """Raised when the Figma API request fails."""


def fetch_file(file_key, token=None):
    normalized_key = (file_key or "").strip()
    if not normalized_key:
        raise FigmaApiError("File key is required.")

    if normalized_key.lower() == "demo":
        return build_demo_file()
    if normalized_key.lower() == "demo-master":
        return build_demo_master_file()

    if not token:
        raise FigmaApiError("A Figma personal access token is required for live analysis.")

    url = f"{FIGMA_API_BASE}/files/{urllib.parse.quote(normalized_key, safe='')}"
    request = urllib.request.Request(
        url,
        headers={
            "X-Figma-Token": token,
            "Accept": "application/json",
            "User-Agent": "MAI-Component-Analyzer/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise FigmaApiError(f"Figma API error {error.code}: {message}") from error
    except urllib.error.URLError as error:
        raise FigmaApiError(f"Unable to reach Figma API: {error.reason}") from error
    except socket.timeout as error:
        raise FigmaApiError("Figma file fetch timed out. The file may be too large for full-file analysis.") from error

    try:
        return json.loads(payload)
    except json.JSONDecodeError as error:
        raise FigmaApiError("Figma API returned invalid JSON.") from error
