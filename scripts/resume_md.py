#!/usr/bin/env python3
"""resume_md — syntax layer for the Markdown resume SSOT.

Parses a resume Markdown document into a Document tree. Knows nothing about
JSON Resume; see jsonresume_map.py for the semantic mapping.
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


def split_frontmatter(text: str) -> tuple[dict, list[str], int]:
    """Return (frontmatter dict, body lines, 1-based line number of the first body line)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FENCE:
        raise MdError(1, f"document must start with a {FENCE} frontmatter fence")
    for i in range(1, len(lines)):
        if lines[i].strip() == FENCE:
            try:
                fm = tomllib.loads("\n".join(lines[1:i]))
            except tomllib.TOMLDecodeError as exc:
                raise MdError(1, f"frontmatter TOML error: {exc}") from exc
            return fm, lines[i + 1:], i + 2
    raise MdError(1, f"unterminated {FENCE} frontmatter fence")


def parse_meta_block(lines: list[str], start: int, line_offset: int) -> tuple[dict, int]:
    """Parse a <!--meta ... --> block starting at lines[start].

    Returns (meta dict, index just past the closing marker). line_offset is the
    1-based source line number of lines[0], used for error reporting.
    """
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == META_CLOSE:
            try:
                meta = tomllib.loads("\n".join(lines[start + 1:j]))
            except tomllib.TOMLDecodeError as exc:
                raise MdError(line_offset + start, f"meta TOML error: {exc}") from exc
            return meta, j + 1
    raise MdError(line_offset + start, f"unterminated {META_OPEN} block")


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


def fingerprint(text: str) -> str:
    """First 4 hex chars of the SHA-256 of the whitespace-normalised text."""
    normalised = " ".join(text.split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:4]


def parse_bullet(line: str, lineno: int) -> Bullet:
    m = BULLET_RE.match(line)
    if not m:
        raise MdError(lineno, "expected a '- ' bullet")
    rest = m.group("rest")

    bullet_id = src = src_hash = None
    src_m = SRC_RE.search(rest)
    if src_m:
        src, src_hash = src_m.group("id"), src_m.group("hash")
        rest = rest[: src_m.start()]
    id_m = ID_RE.search(rest)
    if id_m:
        bullet_id = id_m.group("id")
        rest = rest[: id_m.start()]

    return Bullet(text=rest.strip(), line=lineno, id=bullet_id, src=src, src_hash=src_hash)
