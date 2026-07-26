#!/usr/bin/env python3
"""cv-pagecheck — a facet resume must be exactly one page.

The renderer used to enforce this by silently dropping bullets past a cap, so
the PDF showed less than the Markdown said and less than the JSON published to
the Gist. Curation now lives in the Markdown; this checks the result instead,
which fails out loud and names the file to trim.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RESUME_DIR = Path(__file__).resolve().parent.parent / "docs" / "resume"
PAGE_RE = re.compile(rb"/Type\s*/Page[^s]")


def page_count(pdf: Path) -> int:
    return len(PAGE_RE.findall(pdf.read_bytes()))


def main() -> int:
    facets = sorted(RESUME_DIR.glob("resume-*.pdf"))
    if not facets:
        print("  (no facet PDFs to check)")
        return 0

    over = [(f, n) for f in facets if (n := page_count(f)) != 1]
    for pdf, n in over:
        print(
            f"✗ {pdf.name} is {n} pages — a facet resume must be one page. "
            f"Trim {pdf.with_suffix('.md').name}: drop a bullet, a project, or a "
            f"skills category (the left sidebar is usually what overruns).",
            file=sys.stderr,
        )
    if over:
        return 1
    print(f"  ✓ all {len(facets)} facet resumes are one page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
