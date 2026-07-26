#!/usr/bin/env python3
"""cv-lint — the gates that keep the Markdown resume set honest and in sync.

Checks, in order:
  1. invariants  — contact / employer / dates / education / languages agree across all files
  2. provenance  — every facet bullet cites a live cv.md bullet ID with a current fingerprint
  3. numbers     — every number in facet text is grounded in the cv.md text it derives from
  4. banned terms— docs/resume/rules.toml patterns, over every published string
  5. freshness   — the committed JSON matches what the Markdown builds to
  6. portal copy — apps/portal/src/data/resume.json (a third publishing surface,
                   deployed by portal-deploy.yml on any push under
                   apps/portal/src/**) matches what cv.md builds to
  7. curation    — a facet's Summary and label are cv.md's with words deleted,
                   never newly written prose

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
# `make cv-publish` ends by copying docs/resume/cv.json here. The file is
# tracked, and .github/workflows/portal-deploy.yml deploys on any push under
# apps/portal/src/** — which includes it. That makes it a third public
# surface (alongside the PDF and the Gist) that nothing had ever gated.
PORTAL_JSON = Path(__file__).resolve().parent.parent / "apps" / "portal" / "src" / "data" / "resume.json"
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

# Fields a facet may never tailor. Contact is the obvious half — an email or a
# phone number that drifts is a resume that cannot be answered. ``profiles``,
# ``url`` and ``image`` are the other half: they are *attribution*, and a facet
# that quietly points its LinkedIn, homepage or avatar somewhere else is
# claiming a different person's identity just as effectively as a changed email.
# ``label`` / ``summary`` / ``work[].summary`` deliberately stay out: they are
# the facet's pitch and are meant to differ per audience. The rules and numbers
# gates police those instead.
BASICS_KEYS = ("name", "email", "phone", "location", "profiles", "url", "image")
WORK_KEYS = ("name", "position", "startDate", "endDate", "location", "url")


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
    message of any non-bullet finding, because "line 27" alone does not say
    whether the operator is looking for a summary paragraph, an entry's
    paragraph or a frontmatter field.

    ``line`` is the text's own line wherever the source has one. Prose gets it
    from ``Section.prose_line`` / ``Entry.prose_line``; a frontmatter value is
    the one case that has none — the parser hands back a TOML dict, not a
    position — so it is anchored to line 1 and its ``where`` says so rather
    than let the operator read line 1 as a real location.
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


FRONTMATTER_CAVEAT = "no line of its own; anchored to line 1"


def _prose_where(heading: str, prose_line: int | None) -> str:
    """Name a prose block, disclosing a heading anchor only if that is all there is.

    ``prose_line`` is set for every non-empty prose block the current parser
    produces, so the caveat branch is unreachable in practice — it stays
    because a silently-wrong line is worse than a wordy one, and the fallback
    to ``Section.line`` above it must never start lying by omission.
    """
    if prose_line is None:
        return f"'{heading}' prose (line is its heading; the prose follows below)"
    return f"'{heading}' prose"


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
            # wrong place. The 'where' string says so, because unlike a prose
            # finding this line really is not the text's.
            texts.append(Text(
                "frontmatter", value, 1, f"frontmatter '{key}' ({FRONTMATTER_CAVEAT})"))

    for section in doc.sections:
        if section.prose:
            texts.append(Text(
                "section-prose", section.prose, section.prose_line or section.line,
                _prose_where(section.title, section.prose_line), section=section.title,
            ))
        for entry in section.entries:
            entry_id = entry.meta.get("id")
            if entry.prose:
                texts.append(Text(
                    "entry-prose", entry.prose, entry.prose_line or entry.line,
                    _prose_where(entry.heading, entry.prose_line), section.title, entry_id,
                ))
            for bullet in entry.bullets:
                texts.append(Text(
                    "bullet", bullet.text, bullet.line, "bullet",
                    section.title, entry_id, bullet,
                ))
    return texts, None


def _all_bullets(md_path: Path) -> tuple[list[Text], Problem | None]:
    """Return every bullet in the document as a ``Text`` (section + entry + Bullet)."""
    texts, problem = _all_texts(md_path)
    return [t for t in texts if t.kind == "bullet"], problem


def _cv_bullets(cv_md: Path) -> tuple[dict[str, str], dict[str, str | None], list[Problem]]:
    """(bullet ID -> text, bullet ID -> owning entry ID), reporting duplicates.

    The owner map is read off the cv.md tree rather than derived from the ID.
    Bullet IDs read ``<entry-id>-h<n>``, but an entry slug may itself contain
    hyphens (``42-vienna-tutor-h1``), so ``id.split("-")[0]`` would name the
    wrong entry — and would do it silently, on exactly the entries whose names
    are least standard.
    """
    index: dict[str, str] = {}
    owners: dict[str, str | None] = {}
    bullets, problem = _all_bullets(cv_md)
    problems: list[Problem] = [problem] if problem is not None else []
    for t in bullets:
        bullet = t.bullet
        if bullet.id is None:
            continue
        if bullet.id in index:
            problems.append(Problem(cv_md.name, bullet.line, f"duplicate bullet ID '{bullet.id}'"))
            continue
        index[bullet.id] = bullet.text
        owners[bullet.id] = t.entry_id
    return index, owners, problems


def cv_index(cv_md: Path) -> tuple[dict[str, str], list[Problem]]:
    """Map bullet ID -> text, reporting duplicates."""
    index, _owners, problems = _cv_bullets(cv_md)
    return index, problems


def check_provenance(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """Every facet highlight must cite a live cv.md bullet with a current fingerprint.

    "Live and current" is not enough on its own. A fresh anchor proves the
    cited sentence still exists and still reads the way it did; it says nothing
    about whether it belongs *here*. Moving a MediaTek achievement under the
    c-sense entry, anchor and all, used to pass every gate — which is precisely
    what an assistant reshuffling a facet does. So the cited bullet must also
    be owned by the entry the citing bullet sits in.
    """
    index, owners, problems = _cv_bullets(cv_md)
    for md in facet_mds:
        bullets, problem = _all_bullets(md)
        if problem is not None:
            problems.append(problem)
            continue
        for t in bullets:
            section, bullet = t.section, t.bullet
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
            owner = owners.get(bullet.src)
            if owner != t.entry_id:
                problems.append(Problem(
                    md.name, bullet.line,
                    f"src '{bullet.src}' belongs to entry '{owner}', not "
                    f"'{t.entry_id}' — cite a bullet from this entry, or move the "
                    f"claim to the entry that earned it",
                ))
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


def load_rules(path: Path | None = None) -> dict:
    # Resolved at call time, not at def time, so RESUME_DIR/RULES_FILE can be
    # redirected (tests point the whole gate set at a throwaway corpus).
    path = RULES_FILE if path is None else path
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


PORTAL_LABEL = "apps/portal/src/data/resume.json"


def check_portal_copy(cv_md: Path, portal_json: Path | None = None) -> list[Problem]:
    """The portal's published copy of the resume must equal what cv.md builds to.

    Resolved at call time against the module-level ``PORTAL_JSON`` (like
    ``load_rules`` does for ``RULES_FILE``), so tests can redirect it. A
    missing file is reported, not raised: this repo can legitimately be
    cloned without ``apps/portal`` present, and a missing file is not the
    same defect as a stale one, so it is a warning rather than fatal — same
    severity model as every other gate here, meaning plain ``cv-lint`` stays
    quiet about it but ``--strict`` still blocks on it, like any warning.
    """
    portal_json = PORTAL_JSON if portal_json is None else portal_json
    if not portal_json.exists():
        return [Problem(
            PORTAL_LABEL, None,
            "not found — this clone has no portal copy to check", fatal=False,
        )]
    built, build_problems = _data_of(cv_md)
    if built is None:
        return build_problems
    committed = json.loads(portal_json.read_text(encoding="utf-8"))
    if built != committed:
        return [Problem(
            PORTAL_LABEL, None,
            "is out of date with docs/resume/cv.json — run `make cv-publish` to "
            "refresh it (never hand-edit the portal copy)",
        )]
    return []


CURATION_WORD_RE = re.compile(r"[a-z0-9+]+")


def _is_subsequence(sub: list[str], base: list[str]) -> str | None:
    """Return the first word of `sub` that is not reachable in order, or None."""
    it = iter(base)
    for word in sub:
        if word not in it:
            return word
    return None


def check_curation(cv_md: Path, facet_mds: list[Path]) -> list[Problem]:
    """A facet's Summary and label must be cv.md's, with words removed.

    A facet reframes the CV — but only its *bullets* do, and those are held to
    account by the provenance, numbers and rules gates. The Summary paragraph and
    the frontmatter label had no such tie: they became `basics.summary` and
    `basics.label`, the two things a reader meets first, with nothing checking
    that they said what the CV says. Newly authored prose slipped in there twice.

    The rule is deliberately crude: the facet's words must appear in the CV's, in
    order. Deleting a clause is curation and passes; writing a new phrase does
    not. Punctuation is free, so ending a sentence early where a clause was cut
    is fine.
    """
    cv_doc, problem = _try_parse(cv_md)
    if cv_doc is None:
        return [problem]
    cv_summary = next(
        (s.prose for s in cv_doc.sections if s.title == "Summary"), "")
    base = {
        "Summary": CURATION_WORD_RE.findall(cv_summary.lower()),
        "label": CURATION_WORD_RE.findall(
            str(cv_doc.frontmatter.get("label", "")).lower()),
    }

    problems: list[Problem] = []
    for md in facet_mds:
        doc, problem = _try_parse(md)
        if doc is None:
            problems.append(problem)
            continue
        section = next((s for s in doc.sections if s.title == "Summary"), None)
        candidates = [
            ("Summary", section.prose if section else "",
             (section.prose_line or section.line) if section else 1),
            ("label", str(doc.frontmatter.get("label", "")), 1),
        ]
        for kind, text, line in candidates:
            if not text:
                continue
            stray = _is_subsequence(CURATION_WORD_RE.findall(text.lower()), base[kind])
            if stray is not None:
                where = kind if kind == "Summary" else "frontmatter 'label'"
                problems.append(Problem(
                    md.name, line,
                    f"{where}: '{stray}' is not in cv.md's {kind} — a facet curates "
                    f"the CV by deleting from it, never by writing new wording. "
                    f"Cut what this audience does not need, or add the claim to "
                    f"cv.md first.",
                ))
    return problems


USAGE = "usage: cv_lint.py [--strict]"


def main(argv: list[str] | None = None) -> int:
    """Run every gate. ``--strict`` promotes warnings to blocking findings.

    Warnings are non-fatal on purpose: a reworded cv.md bullet leaves a stale
    anchor behind, and blocking on that would make ordinary editing miserable.
    But "non-fatal" was being read as "ignorable" by the two targets that ship
    an artifact — a gutted cv.md bullet with the strong claim still standing in
    the facet went out to the Gist under a plain ⚠. Anything that leaves the
    working copy runs ``--strict``; ``make cv-lint`` stays lenient.
    """
    argv = sys.argv[1:] if argv is None else argv
    strict = "--strict" in argv
    unknown = [a for a in argv if a != "--strict"]
    if unknown:
        print(f"✗ unrecognised argument(s): {' '.join(unknown)}\n{USAGE}", file=sys.stderr)
        return 2
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
        + check_portal_copy(CV_MD)
        + check_curation(CV_MD, facets)
    )

    for p in problems:
        print(p.render(), file=sys.stderr)
    if any(p.fatal for p in problems):
        return 1
    if strict and problems:
        print(
            f"✗ --strict: {len(problems)} warning(s) block a publishing path — "
            f"resolve them, or run `make cv-lint` while you iterate",
            file=sys.stderr,
        )
        return 1
    print(f"✓ invariants consistent across cv.md + {len(facets)} resume(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
