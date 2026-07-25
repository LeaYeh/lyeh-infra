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

import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from jsonresume_map import to_jsonresume
from resume_md import Bullet, Document, MdError, fingerprint, parse

RESUME_DIR = Path(__file__).resolve().parent.parent / "docs" / "resume"
CV_MD = RESUME_DIR / "cv.md"
RULES_FILE = RESUME_DIR / "rules.toml"
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:[.,]\d+)*(?:[xX×]|[KkMmBb])?(?![A-Za-z0-9])"
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


def _try_parse(md_path: Path) -> tuple[Document | None, Problem | None]:
    """Parse ``md_path``, turning a syntax error into a ``Problem``.

    Every gate needs this: an ordinary mid-edit mistake must be reported
    through the same ``✗ file:line message`` path as any other finding —
    not as a raw traceback — and a parse failure in one document must not
    abort the checks for every other document.
    """
    try:
        return parse(md_path.read_text(encoding="utf-8")), None
    except MdError as exc:
        return None, Problem(md_path.name, exc.line, exc.message)


def _data_of(md_path: Path) -> tuple[dict | None, list[Problem]]:
    """Parse + map ``md_path`` to JSON Resume data.

    Returns (data, problems). ``data`` is None if the document could not be
    parsed or mapped, in which case the caller must skip it rather than
    treat a missing dict as an empty one.
    """
    doc, problem = _try_parse(md_path)
    if problem is not None:
        return None, [problem]
    try:
        data, _ = to_jsonresume(doc)
    except MdError as exc:
        return None, [Problem(md_path.name, exc.line, exc.message)]
    return data, []


def check_invariants(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """Fields that must never be tailored have to match cv.md exactly."""
    ref_data, problems = _data_of(cv_md)
    if ref_data is None:
        return problems
    ref = _invariants(ref_data)
    for md in facet_mds:
        cur_data, cur_problems = _data_of(md)
        if cur_data is None:
            problems.extend(cur_problems)
            continue
        cur = _invariants(cur_data)
        for section in ("basics", "work", "education", "languages"):
            if cur[section] != ref[section]:
                problems.append(Problem(
                    md.name, None,
                    f"'{section}' drifts from cv.md — invariant fields must be copied verbatim",
                ))
    return problems


def _all_bullets(md_path: Path) -> tuple[list[tuple[str, Bullet]], Problem | None]:
    """Return every bullet in the document, with its section title.

    A malformed document is reported as a ``Problem`` instead of raised, so
    one bad file cannot abort the gates for every other file.
    """
    doc, problem = _try_parse(md_path)
    if problem is not None:
        return [], problem
    bullets = [
        (section.title, bullet)
        for section in doc.sections
        for entry in section.entries
        for bullet in entry.bullets
    ]
    return bullets, None


def cv_index(cv_md: Path) -> tuple[dict[str, str], list[Problem]]:
    """Map bullet ID -> text, reporting duplicates."""
    index: dict[str, str] = {}
    bullets, problem = _all_bullets(cv_md)
    problems: list[Problem] = [problem] if problem is not None else []
    for _, bullet in bullets:
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
        bullets, problem = _all_bullets(md)
        if problem is not None:
            problems.append(problem)
            continue
        for section, bullet in bullets:
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
        bullets, problem = _all_bullets(md)
        if problem is not None:
            problems.append(problem)
            continue
        for _, bullet in bullets:
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
    real metric, not an identifier fragment. A single trailing magnitude
    letter (``K``/``M``/``B``, either case) is also kept as part of the token
    — "14K" is a claim, not an identifier — while any other trailing letter
    (e.g. ``3D``) still excludes the digits from being a claim.
    """
    return NUMBER_RE.findall(URL_RE.sub("", text))


def check_numbers(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """A facet bullet may not introduce a number its source bullet does not contain."""
    index, _ = cv_index(cv_md)          # duplicate-ID problems are check_provenance's job
    problems: list[Problem] = []
    for md in facet_mds:
        bullets, problem = _all_bullets(md)
        if problem is not None:
            problems.append(problem)
            continue
        for _, bullet in bullets:
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


def check_freshness(mds: list[Path]) -> list[Problem]:
    """The committed JSON must equal what the Markdown builds to."""
    problems: list[Problem] = []
    for md in mds:
        out = md.with_suffix(".json")
        if not out.exists():
            problems.append(Problem(out.name, None, "missing — run `make cv-build`"))
            continue
        built, build_problems = _data_of(md)
        if built is None:
            problems.extend(build_problems)
            continue
        committed = json.loads(out.read_text(encoding="utf-8"))
        if built != committed:
            problems.append(Problem(
                out.name, None, "is out of date with the Markdown — run `make cv-build`"))
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
        + check_freshness([CV_MD] + facets)
    )

    for p in problems:
        print(p.render(), file=sys.stderr)
    if any(p.fatal for p in problems):
        return 1
    print(f"✓ invariants consistent across cv.md + {len(facets)} resume(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
