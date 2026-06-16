# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic", "requests"]
# ///

import json
import os
import re
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


def _parse_path(path: str) -> list[str | int]:
    """Parse 'work[0].highlights' → ['work', 0, 'highlights']."""
    tokens: list[str | int] = []
    for part in path.split("."):
        m = re.match(r"^(\w+)\[(\d+)\]$", part)
        if m:
            tokens.append(m.group(1))
            tokens.append(int(m.group(2)))
        else:
            tokens.append(part)
    return tokens


def apply_patch(resume: dict, field: str, action: str, value) -> None:
    tokens = _parse_path(field)
    obj = resume
    for token in tokens[:-1]:
        obj = obj[token]
    last = tokens[-1]
    if action == "append":
        obj[last].append(value)
    else:
        obj[last] = value
