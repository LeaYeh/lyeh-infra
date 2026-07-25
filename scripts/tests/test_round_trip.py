import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from cv_build import build_data

RESUME_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "resume"
NAMES = ["cv", "resume-a", "resume-b", "resume-c"]


def pre_migration(name: str) -> dict:
    """The committed JSON as of the last commit before the Markdown migration."""
    blob = subprocess.run(
        ["git", "show", f"HEAD:docs/resume/{name}.json"],
        capture_output=True, text=True, check=True, cwd=RESUME_DIR,
    ).stdout
    return json.loads(blob)


@pytest.mark.parametrize("name", NAMES)
def test_markdown_builds_back_to_the_original_json(name):
    data, errors = build_data(RESUME_DIR / f"{name}.md")
    assert errors == [], [f"{e.line}: {e.message}" for e in errors]
    assert data == pre_migration(name)
