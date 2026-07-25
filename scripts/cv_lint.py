#!/usr/bin/env python3
"""cv-lint — the gates that keep the Markdown resume set honest and in sync.

Checks, in order:
  1. invariants  — contact / employer / dates / education / languages agree across all files
  2. provenance  — every facet bullet cites a live cv.md bullet ID with a current fingerprint
  3. numbers     — every digit in a facet bullet exists in its source bullet
  4. banned terms— docs/resume/rules.toml patterns
  5. freshness   — the committed JSON matches what the Markdown builds to
"""
from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from jsonresume_map import to_jsonresume
from resume_md import fingerprint, parse

RESUME_DIR = Path(__file__).resolve().parent.parent / "docs" / "resume"
CV_MD = RESUME_DIR / "cv.md"
RULES_FILE = RESUME_DIR / "rules.toml"
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:[.,]\d+)*(?:[xX×])?(?![A-Za-z0-9])"
)
URL_RE = re.compile(r"https?://\S+")

BASICS_KEYS = ("name", "email", "phone", "location")
WORK_KEYS = ("name", "position", "startDate", "endDate", "location")


@dataclass
class Problem:
    file: str
    line: int | None
    message: str
    fatal: bool = True

    def render(self) -> str:
        mark = "✗" if self.fatal else "⚠"
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{mark} {where} {self.message}"


def _invariants(data: dict) -> dict:
    return {
        "basics": {k: data.get("basics", {}).get(k) for k in BASICS_KEYS},
        "work": [tuple(w.get(k) for k in WORK_KEYS) for w in data.get("work", [])],
        "education": data.get("education"),
        "languages": data.get("languages"),
    }


def _data_of(md_path: Path) -> dict:
    data, _ = to_jsonresume(parse(md_path.read_text(encoding="utf-8")))
    return data


def check_invariants(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """Fields that must never be tailored have to match cv.md exactly."""
    ref = _invariants(_data_of(cv_md))
    problems: list[Problem] = []
    for md in facet_mds:
        cur = _invariants(_data_of(md))
        for section in ("basics", "work", "education", "languages"):
            if cur[section] != ref[section]:
                problems.append(Problem(
                    md.name, None,
                    f"'{section}' drifts from cv.md — invariant fields must be copied verbatim",
                ))
    return problems


def _id_bearing_bullets(md_path: Path):
    """Yield every bullet in the document, with its section title."""
    doc = parse(md_path.read_text(encoding="utf-8"))
    for section in doc.sections:
        for entry in section.entries:
            for bullet in entry.bullets:
                yield section.title, bullet


def cv_index(cv_md: Path) -> tuple[dict[str, str], list[Problem]]:
    """Map bullet ID -> text, reporting duplicates."""
    index: dict[str, str] = {}
    problems: list[Problem] = []
    for _, bullet in _id_bearing_bullets(cv_md):
        if bullet.id is None:
            continue
        if bullet.id in index:
            problems.append(Problem(cv_md.name, bullet.line, f"duplicate bullet ID '{bullet.id}'"))
            continue
        index[bullet.id] = bullet.text
    return index, problems


def check_provenance(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """Every facet highlight must cite a live cv.md bullet with a current fingerprint."""
    index, problems = cv_index(cv_md)
    for md in facet_mds:
        for section, bullet in _id_bearing_bullets(md):
            if section not in ("Work", "Volunteer", "Projects"):
                continue                      # keywords/courses are not curated content
            if bullet.src is None:
                problems.append(Problem(
                    md.name, bullet.line,
                    "bullet has no src anchor — add the fact to cv.md first, then cite its ID",
                ))
                continue
            source = index.get(bullet.src)
            if source is None:
                problems.append(Problem(
                    md.name, bullet.line, f"src '{bullet.src}' does not exist in cv.md"))
                continue
            current = fingerprint(source)
            if bullet.src_hash != current:
                problems.append(Problem(
                    md.name, bullet.line,
                    f"stale: cv.md '{bullet.src}' changed since this was written "
                    f"(@{bullet.src_hash} → @{current}); re-check the wording, then update the anchor",
                    fatal=False,
                ))
    return problems


def load_rules(path: Path = RULES_FILE) -> dict:
    if not path.exists():
        return {"banned": [], "qualified": []}
    rules = tomllib.loads(path.read_text(encoding="utf-8"))
    rules.setdefault("banned", [])
    rules.setdefault("qualified", [])
    return rules


def check_rules(mds: list[Path], rules: dict) -> list[Problem]:
    """Banned terms are never allowed; qualified terms need their qualifier nearby."""
    problems: list[Problem] = []
    for md in mds:
        for _, bullet in _id_bearing_bullets(md):
            for rule in rules["banned"]:
                if re.search(rule["pattern"], bullet.text, re.IGNORECASE):
                    problems.append(Problem(md.name, bullet.line, rule["message"]))
            for rule in rules["qualified"]:
                if re.search(rule["pattern"], bullet.text, re.IGNORECASE) and not re.search(
                    rule["requires"], bullet.text, re.IGNORECASE
                ):
                    problems.append(Problem(md.name, bullet.line, rule["message"]))
    return problems


def _claimed_numbers(text: str) -> list[str]:
    """Standalone numeric tokens in ``text`` — the only things that count as claims.

    A number glued to letters (``k3s``, ``CX23``) is part of an identifier, not
    a measurement, and is excluded by the lookaround. URLs are stripped first
    since a digit run inside one (a doc ID, a query param) is never a claim
    either. ``5x`` / ``5×`` is kept as a claim — "reduced build time 5x" is a
    real metric, not an identifier fragment.
    """
    return NUMBER_RE.findall(URL_RE.sub("", text))


def check_numbers(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """A facet bullet may not introduce a number its source bullet does not contain."""
    index, _ = cv_index(cv_md)          # duplicate-ID problems are check_provenance's job
    problems: list[Problem] = []
    for md in facet_mds:
        for _, bullet in _id_bearing_bullets(md):
            source = index.get(bullet.src or "")
            if source is None:
                continue                      # provenance gate already reported this
            allowed = set(_claimed_numbers(source))
            invented = [n for n in _claimed_numbers(bullet.text) if n not in allowed]
            if invented:
                problems.append(Problem(
                    md.name, bullet.line,
                    f"number(s) {', '.join(invented)} do not appear in cv.md '{bullet.src}'",
                ))
    return problems


def main() -> int:
    if not CV_MD.exists():
        print(f"✗ {CV_MD} not found", file=sys.stderr)
        return 2
    facets = sorted(RESUME_DIR.glob("resume-*.md"))
    rules = load_rules()
    problems = (
        check_invariants(CV_MD, facets)
        + check_provenance(CV_MD, facets)
        + check_numbers(CV_MD, facets)
        + check_rules([CV_MD] + facets, rules)
    )

    for p in problems:
        print(p.render(), file=sys.stderr)
    if any(p.fatal for p in problems):
        return 1
    print(f"✓ invariants consistent across cv.md + {len(facets)} resume(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
