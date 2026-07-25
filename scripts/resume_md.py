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
