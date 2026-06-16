# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic", "requests"]
# ///

import json
import os
from pathlib import Path

import requests


def load_env(env_file: Path | None = None) -> None:
    if env_file is None:
        env_file = Path(__file__).parent / "cv-sync.env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), val)


def load_content(content_dir: Path | None = None) -> str:
    if content_dir is None:
        content_dir = Path(__file__).parent.parent / "apps/portal/src/content"
    files = [
        content_dir / "about.md",
        *sorted((content_dir / "posts").glob("*.md")),
        *sorted((content_dir / "projects").glob("*.md")),
    ]
    parts = []
    for f in files:
        if f.name == "_index.md" or not f.exists():
            continue
        parts.append(f"--- {f.relative_to(content_dir)} ---\n{f.read_text()}")
    return "\n\n".join(parts)


def fetch_gist(gist_id: str, token: str) -> tuple[dict, str]:
    resp = requests.get(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
    )
    resp.raise_for_status()
    for filename, file_data in resp.json()["files"].items():
        if filename.endswith(".json"):
            return json.loads(file_data["content"]), filename
    raise ValueError(f"No JSON file found in gist {gist_id}")


def update_gist(gist_id: str, token: str, filename: str, resume: dict) -> None:
    resp = requests.patch(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
        json={"files": {filename: {"content": json.dumps(resume, indent=2, ensure_ascii=False)}}},
    )
    resp.raise_for_status()
