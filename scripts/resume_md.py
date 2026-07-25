#!/usr/bin/env python3
"""resume_md — syntax layer for the Markdown resume SSOT.

Parses a resume Markdown document into a Document tree. Knows nothing about
JSON Resume; see jsonresume_map.py for the semantic mapping.

Grammar notes that are deliberate rather than incidental:

* A node (section or entry) carries at most **one** prose paragraph. A second
  paragraph is a hard error, not a silent drop: the operator wrote text that
  would otherwise vanish from the rendered PDF and the published Gist with no
  diagnostic. If a node needs more prose, the sentences belong in one paragraph
  or in bullets.
* An entry carries at most **one** ``<!--meta`` block, for the same reason.
* ``<!--meta`` must stand alone on its opening line. Freeform HTML comments are
  not part of this grammar, so a line that merely starts with ``<!--meta``
  (``<!--metadata ...``, ``<!--meta id = "x"``) is an error rather than prose.
"""
from __future__ import annotations

import hashlib
import re
import tomllib
from dataclasses import dataclass, field

FENCE = "+++"
META_OPEN = "<!--meta"
META_CLOSE = "-->"


class MdError(Exception):
    """A syntax error anchored to a 1-based line number in the source document."""

    def __init__(self, line: int, message: str):
        super().__init__(f"line {line}: {message}")
        self.line = line
        self.message = message


def split_lines(text: str) -> list[str]:
    """Split on exactly the two line endings this grammar recognises: CRLF and LF.

    str.splitlines() also breaks on \\x0c, U+2028 and U+0085, which would shift
    every subsequent line number by one and send the operator to the wrong line.
    """
    return text.replace("\r\n", "\n").split("\n")


def _toml_error_line(exc: Exception, toml_first_line: int, fallback: int) -> int:
    """Map a TOMLDecodeError onto an absolute source line.

    ``TOMLDecodeError.lineno`` (1-based, relative to the TOML text) exists on
    Python 3.14+; on 3.11-3.13 it is absent and we fall back to the marker line.
    """
    lineno = getattr(exc, "lineno", None)
    if not isinstance(lineno, int):
        return fallback
    return toml_first_line + lineno - 1


def split_frontmatter(text: str) -> tuple[dict, list[str], int]:
    """Return (frontmatter dict, body lines, 1-based line number of the first body line)."""
    lines = split_lines(text)
    if not lines or lines[0].strip() != FENCE:
        raise MdError(1, f"document must start with a {FENCE} frontmatter fence")
    for i in range(1, len(lines)):
        if lines[i].strip() == FENCE:
            try:
                fm = tomllib.loads("\n".join(lines[1:i]))
            except tomllib.TOMLDecodeError as exc:
                # The frontmatter TOML text starts on source line 2.
                raise MdError(
                    _toml_error_line(exc, toml_first_line=2, fallback=1),
                    f"frontmatter TOML error: {exc}",
                ) from exc
            return fm, lines[i + 1:], i + 2
    raise MdError(1, f"unterminated {FENCE} frontmatter fence")


def parse_meta_block(lines: list[str], start: int, line_offset: int) -> tuple[dict, int]:
    """Parse a <!--meta ... --> block starting at lines[start].

    Returns (meta dict, index just past the closing marker). line_offset is the
    1-based source line number of lines[0], used for error reporting.
    """
    open_line = line_offset + start
    if lines[start].strip() != META_OPEN:
        raise MdError(
            open_line,
            f"the {META_OPEN} marker must stand alone on its line; "
            f"put the TOML on the following lines",
        )
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == META_CLOSE:
            try:
                meta = tomllib.loads("\n".join(lines[start + 1:j]))
            except tomllib.TOMLDecodeError as exc:
                # The meta TOML text starts one line after the marker.
                raise MdError(
                    _toml_error_line(exc, toml_first_line=open_line + 1, fallback=open_line),
                    f"meta TOML error: {exc}",
                ) from exc
            return meta, j + 1
    raise MdError(open_line, f"unterminated {META_OPEN} block")


BULLET_RE = re.compile(r"^-\s+(?P<rest>.+?)\s*$")
ID_RE = re.compile(r"\s*\{#(?P<id>[A-Za-z0-9._-]+)\}$")
SRC_RE = re.compile(r"\s*<!--\s*src:\s*(?P<id>[A-Za-z0-9._-]+)\s*@(?P<hash>[0-9a-f]{4})\s*-->$")


@dataclass
class Bullet:
    text: str
    line: int
    id: str | None = None
    src: str | None = None
    src_hash: str | None = None


ANNOTATION_HELP = (
    "the only annotations a bullet may carry are '{#some-id}' and "
    "'<!-- src: some-id @abcd -->' (hash is exactly 4 lowercase hex characters)"
)


def fingerprint(text: str) -> str:
    """First 4 hex chars of the SHA-256 of the whitespace-normalised text.

    Callers must pass ``Bullet.text`` — that is, the bullet body *after* the
    ``{#id}`` and ``<!-- src: ... -->`` annotations have been stripped.
    Fingerprinting the raw Markdown line instead would make every anchor
    mismatch and turn the staleness check into noise.
    """
    normalised = " ".join(text.split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:4]


def parse_bullet(line: str, lineno: int) -> Bullet:
    m = BULLET_RE.match(line)
    if not m:
        raise MdError(lineno, "expected a '- ' bullet")
    rest = m.group("rest")

    bullet_id = src = src_hash = None
    # Strip trailing annotations in whichever order the operator wrote them.
    while True:
        src_m = SRC_RE.search(rest) if src is None else None
        if src_m:
            src, src_hash = src_m.group("id"), src_m.group("hash")
            rest = rest[: src_m.start()]
            continue
        id_m = ID_RE.search(rest) if bullet_id is None else None
        if id_m:
            bullet_id = id_m.group("id")
            rest = rest[: id_m.start()]
            continue
        break

    text = rest.strip()
    if text.endswith(META_CLOSE) or text.endswith("}"):
        # A malformed annotation would otherwise survive into Bullet.text, be
        # fingerprinted, be rendered into the PDF, and make the provenance gate
        # report "no source anchor" at a line that visibly has one.
        raise MdError(lineno, f"malformed bullet annotation: {ANNOTATION_HELP}")

    return Bullet(text=text, line=lineno, id=bullet_id, src=src, src_hash=src_hash)


@dataclass
class Entry:
    heading: str
    line: int
    meta: dict = field(default_factory=dict)
    prose: str = ""
    bullets: list[Bullet] = field(default_factory=list)


@dataclass
class Section:
    title: str
    line: int
    prose: str = ""
    entries: list[Entry] = field(default_factory=list)


@dataclass
class Document:
    frontmatter: dict
    sections: list[Section] = field(default_factory=list)

    def section(self, title: str) -> Section | None:
        for s in self.sections:
            if s.title == title:
                return s
        return None


def parse(text: str) -> Document:
    frontmatter, body, offset = split_frontmatter(text)
    doc = Document(frontmatter=frontmatter)

    prose: list[str] = []
    prose_line = offset  # source line of the first fragment of the pending paragraph
    section: Section | None = None
    entry: Entry | None = None

    def flush_prose() -> None:
        if not prose:
            return
        joined = " ".join(" ".join(prose).split())
        target = entry if entry is not None else section
        if target is None:
            raise MdError(prose_line, "prose found before the first '# Section' heading")
        if target.prose:
            raise MdError(
                prose_line, f"multiple prose paragraphs in '{target_name(target)}'"
            )
        target.prose = joined
        prose.clear()

    def target_name(target) -> str:
        return getattr(target, "heading", None) or getattr(target, "title", "?")

    i = 0
    while i < len(body):
        raw = body[i]
        lineno = offset + i
        stripped = raw.strip()

        if stripped.startswith(META_OPEN):
            if entry is None:
                raise MdError(lineno, "meta block must follow a '## ' entry heading")
            if entry.meta:
                raise MdError(lineno, f"multiple meta blocks in '{entry.heading}'")
            flush_prose()
            entry.meta, consumed = parse_meta_block(body, i, offset)
            i = consumed
            continue

        if stripped.startswith("## "):
            flush_prose()
            if section is None:
                raise MdError(lineno, "'## ' entry found before any '# Section' heading")
            entry = Entry(heading=stripped[3:].strip(), line=lineno)
            section.entries.append(entry)
        elif stripped.startswith("# "):
            flush_prose()
            entry = None
            section = Section(title=stripped[2:].strip(), line=lineno)
            doc.sections.append(section)
        elif BULLET_RE.match(stripped):
            flush_prose()
            if entry is None:
                if section is None:
                    raise MdError(lineno, "bullet found before any '# Section' heading")
                raise MdError(lineno, f"bullet in section '{section.title}' has no '## ' entry")
            entry.bullets.append(parse_bullet(stripped, lineno))
        elif stripped:
            if not prose:
                prose_line = lineno
            prose.append(stripped)
        else:
            flush_prose()
        i += 1

    flush_prose()
    return doc
