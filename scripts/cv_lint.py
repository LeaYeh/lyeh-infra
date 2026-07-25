#!/usr/bin/env python3
"""cv-lint — the gates that keep the Markdown resume set honest and in sync.

Checks, in order:
  1. invariants  — contact / employer / dates / education / languages agree across all files
  2. provenance  — every facet bullet cites a live cv.md bullet ID with a current fingerprint
  3. numbers     — every number in facet text is grounded in the cv.md text it derives from
  4. banned terms— docs/resume/rules.toml patterns, over every published string
  5. freshness   — the committed JSON matches what the Markdown builds to

Bullets are not the document. About half of what reaches the JSON is prose or
frontmatter — ``# Summary`` prose becomes ``basics.summary``, entry prose
becomes ``work[].summary`` / ``projects[].description``, and the frontmatter
``label`` becomes ``basics.label``, the first line a reader sees. ``_all_texts``
is therefore the single definition of "everything in this document a gate must
look at"; the gates filter it rather than each re-deciding what a document is.
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
    r"(?<![A-Za-z0-9])\d+(?:[.,]\d+)*(?:[xX×]|[KkMmBb]|[A-Za-z]{2,3})?(?![A-Za-z0-9])"
)
URL_RE = re.compile(r"https?://\S+")

# Magnitudes a regex cannot ground: "doubled throughput" is a claim with no
# digit in it. These produce a non-fatal warning — the operator is told which
# phrase to check by eye, not blocked.
MAGNITUDE_WORDS = (
    "doubled", "halved", "tripled", "quadrupled",
    "thousand", "million", "billion",
    "twofold", "two-fold", "threefold", "three-fold",
    "order of magnitude",
)
MAGNITUDE_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(w) for w in MAGNITUDE_WORDS) + r")\b", re.IGNORECASE
)

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


FRONTMATTER_TEXT_KEYS = ("label", "summary")


@dataclass(frozen=True)
class Text:
    """One checkable string in a document, with where it came from.

    ``kind`` is one of ``frontmatter`` / ``section-prose`` / ``entry-prose`` /
    ``bullet``. ``where`` names the location for a human; it prefixes the
    message of any non-bullet finding, because a prose or frontmatter finding
    is anchored to a heading line (or to line 1) rather than to the text
    itself, and the line alone would be ambiguous.
    """

    kind: str
    text: str
    line: int
    where: str
    section: str | None = None
    entry_id: str | None = None
    bullet: Bullet | None = None

    @property
    def prefix(self) -> str:
        return "" if self.kind == "bullet" else f"{self.where}: "


def _all_texts(md_path: Path) -> tuple[list[Text], Problem | None]:
    """Every string in the document that reaches the JSON, in source order.

    A malformed document is reported as a ``Problem`` instead of raised, so
    one bad file cannot abort the gates for every other file.
    """
    doc, problem = _try_parse(md_path)
    if problem is not None:
        return [], problem

    texts: list[Text] = []
    for key in FRONTMATTER_TEXT_KEYS:
        value = doc.frontmatter.get(key)
        if isinstance(value, str) and value.strip():
            # A frontmatter value has no line of its own: the parser hands
            # back a TOML dict, not a position. Line 1 (the opening fence) is
            # honest about that; a guessed line would send the operator to the
            # wrong place.
            texts.append(Text("frontmatter", value, 1, f"frontmatter '{key}'"))

    for section in doc.sections:
        if section.prose:
            texts.append(Text(
                "section-prose", section.prose, section.line,
                f"'{section.title}' prose", section=section.title,
            ))
        for entry in section.entries:
            entry_id = entry.meta.get("id")
            if entry.prose:
                texts.append(Text(
                    "entry-prose", entry.prose, entry.line,
                    f"'{entry.heading}' prose", section.title, entry_id,
                ))
            for bullet in entry.bullets:
                texts.append(Text(
                    "bullet", bullet.text, bullet.line, "bullet",
                    section.title, entry_id, bullet,
                ))
    return texts, None


def _all_bullets(md_path: Path) -> tuple[list[tuple[str, Bullet]], Problem | None]:
    """Return every bullet in the document, with its section title."""
    texts, problem = _all_texts(md_path)
    return [(t.section, t.bullet) for t in texts if t.kind == "bullet"], problem


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
    """Banned terms are never allowed; qualified terms need their qualifier nearby.

    Applied to every published string — bullets, entry prose, section prose and
    the frontmatter ``label`` / ``summary``. A claim the rules exist to forbid
    is no less published for being a summary sentence.
    """
    problems: list[Problem] = []
    for md in mds:
        texts, problem = _all_texts(md)
        if problem is not None:
            problems.append(problem)
            continue
        for t in texts:
            for rule in rules["banned"]:
                if re.search(rule["pattern"], t.text, re.IGNORECASE):
                    problems.append(Problem(md.name, t.line, t.prefix + rule["message"]))
            for rule in rules["qualified"]:
                if re.search(rule["pattern"], t.text, re.IGNORECASE) and not re.search(
                    rule["requires"], t.text, re.IGNORECASE
                ):
                    problems.append(Problem(md.name, t.line, t.prefix + rule["message"]))
    return problems


def _claimed_numbers(text: str) -> list[str]:
    """Standalone numeric tokens in ``text`` — the only things that count as claims.

    A number *preceded* by a letter or digit (``k3s``, ``CX23``, ``Python3``,
    ``v1``) is part of an identifier, not a measurement, and is excluded by the
    lookbehind — which is the lookaround that does the real work. URLs are
    stripped first since a digit run inside one (a doc ID, a query param) is
    never a claim either.

    A number *followed* by a short letter run keeps that run inside the token,
    so the token carries its unit: ``200ms``, ``30TB``, ``4GB``, ``3rd``, and
    (via the magnitude branch) ``14K``. Those are the canonical platform and
    SRE metrics; excluding them, as a bare trailing-letter veto did, hid
    exactly the numbers a resume inflates. A single non-magnitude letter is
    still not a unit — ``3D`` is a technique, not a measurement — so the run
    must be at least two letters unless it is ``K``/``M``/``B`` or ``x``/``×``.
    """
    return NUMBER_RE.findall(URL_RE.sub("", text))


def _magnitude_claims(text: str) -> list[str]:
    """Spelled-out magnitudes ("doubled", "order of magnitude"), lowercased."""
    seen: list[str] = []
    for match in MAGNITUDE_RE.findall(text):
        word = match.lower()
        if word not in seen:
            seen.append(word)
    return seen


def _cv_grounding(cv_md: Path) -> tuple[dict[str, str], dict[str, str], str]:
    """Three views of cv.md, one per grounding rule.

    Returns (bullet ID -> bullet text, entry ID -> that entry's prose and all
    of its bullets, the whole document's text). Duplicate-ID problems are
    check_provenance's job, so the first spelling of a bullet ID wins here.
    """
    texts, _ = _all_texts(cv_md)
    bullets: dict[str, str] = {}
    entries: dict[str, str] = {}
    for t in texts:
        if t.kind == "bullet" and t.bullet.id and t.bullet.id not in bullets:
            bullets[t.bullet.id] = t.bullet.text
        if t.entry_id:
            entries[t.entry_id] = f"{entries.get(t.entry_id, '')} {t.text}".strip()
    return bullets, entries, " ".join(t.text for t in texts)


def _grounding(t: Text, bullets: dict[str, str], entries: dict[str, str],
               whole_cv: str) -> tuple[str, str] | None:
    """The cv.md text ``t`` must be grounded in, and how to name it.

    None means "not this gate's business": a bullet with no live source anchor
    is check_provenance's finding, not a number finding reported twice.
    """
    if t.kind == "bullet":
        source = bullets.get(t.bullet.src or "")
        return None if source is None else (source, f"cv.md '{t.bullet.src}'")
    if t.kind == "entry-prose":
        # Prose carries no anchor, so correspondence is by the entry's meta
        # id — the same slug in every document. A missing entry grounds
        # against nothing, which is the correct answer, not a reason to skip.
        return entries.get(t.entry_id or "", ""), f"cv.md entry '{t.entry_id}'"
    # Section prose and frontmatter are a facet-wide pitch with no single
    # source entry: the whole of cv.md is what they must be true of.
    return whole_cv, "cv.md"


def check_numbers(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """A facet may not introduce a number the cv.md text it derives from lacks.

    Only facets are checked: cv.md has nothing above it to be grounded
    against. Comparison is case-insensitive ("14K" and "14k" are the same
    claim) while the message keeps the spelling the facet actually used.
    """
    bullets, entries, whole_cv = _cv_grounding(cv_md)
    problems: list[Problem] = []
    for md in facet_mds:
        texts, problem = _all_texts(md)
        if problem is not None:
            problems.append(problem)
            continue
        for t in texts:
            ground = _grounding(t, bullets, entries, whole_cv)
            if ground is None:
                continue
            source, where = ground

            allowed = {n.lower() for n in _claimed_numbers(source)}
            invented = [n for n in _claimed_numbers(t.text) if n.lower() not in allowed]
            if invented:
                problems.append(Problem(
                    md.name, t.line,
                    f"{t.prefix}number(s) {', '.join(invented)} do not appear in {where}",
                ))

            grounded_words = _magnitude_claims(source)
            vague = [w for w in _magnitude_claims(t.text) if w not in grounded_words]
            if vague:
                problems.append(Problem(
                    md.name, t.line,
                    f"{t.prefix}'{', '.join(vague)}' has no counterpart in {where} — "
                    f"a spelled-out magnitude cannot be checked mechanically; verify by eye",
                    fatal=False,
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
