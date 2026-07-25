#!/usr/bin/env python3
"""cv-build — compile the Markdown resume SSOT into JSON Resume.

Refuses to write any JSON whose schema validation fails; the previous JSON is
left untouched so a broken edit never propagates to the PDF or the Gist.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from jsonresume_map import to_jsonresume
from jsonresume_schema import validate
from resume_md import MdError, parse

RESUME_DIR = Path(__file__).resolve().parent.parent / "docs" / "resume"


@dataclass
class BuildError:
    line: int | None
    message: str

    def render(self, name: str) -> str:
        where = f"{name}:{self.line}" if self.line else name
        return f"✗ {where} {self.message}"


def build_data(md_path: Path) -> tuple[dict | None, list[BuildError]]:
    """Parse and validate. Returns (data, errors); data is None if unparseable."""
    try:
        doc = parse(md_path.read_text(encoding="utf-8"))
        data, lines = to_jsonresume(doc)
    except MdError as exc:
        return None, [BuildError(exc.line, exc.message)]

    errors = []
    for path, message in validate(data):
        line = lines.get(path)
        if line is None:                       # fall back to the owning entry
            line = lines.get(path.rsplit(".", 1)[0])
        errors.append(BuildError(line, f"{path}: {message}"))
    return data, errors


def build_file(md_path: Path) -> list[BuildError]:
    """Build one .md into its sibling .json. Writes nothing if there are errors."""
    data, errors = build_data(md_path)
    if errors or data is None:
        return errors
    out = md_path.with_suffix(".json")
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return []


def main() -> int:
    sources = sorted(RESUME_DIR.glob("cv.md")) + sorted(RESUME_DIR.glob("resume-*.md"))
    if not sources:
        print(f"✗ no Markdown sources in {RESUME_DIR}", file=sys.stderr)
        return 2
    failed = False
    for md in sources:
        errors = build_file(md)
        if errors:
            failed = True
            for err in errors:
                print(err.render(md.name), file=sys.stderr)
        else:
            print(f"  ✓ {md.with_suffix('.json').name}")
    if failed:
        print("\nBUILD FAILED — no JSON was written for the files above.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
