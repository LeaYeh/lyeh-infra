# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic", "requests"]
# ///

import json
import os
import re
from pathlib import Path


def load_env(env_file: Path | None = None) -> None:
    if env_file is None:
        env_file = Path(__file__).parent / "cv-sync.env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


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
