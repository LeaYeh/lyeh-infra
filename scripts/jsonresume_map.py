#!/usr/bin/env python3
"""jsonresume_map — semantic layer: Document -> JSON Resume dict + line map."""
from __future__ import annotations

from dataclasses import dataclass

from resume_md import Document, Entry, MdError, Section

SCHEMA_URL = (
    "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
)
META = {
    "version": "v1.0.0",
    "canonical": "https://github.com/jsonresume/resume-schema/blob/v1.0.0/schema.json",
}

BASICS_KEYS = ("name", "label", "image", "email", "phone", "url", "location", "profiles")
META_ALIASES = {"start": "startDate", "end": "endDate"}


@dataclass(frozen=True)
class SectionSpec:
    key: str                     # JSON Resume top-level key
    heading_fields: tuple        # fields the '## ' heading splits into, on ' — '
    prose_field: str | None      # where the prose paragraph goes
    bullet_field: str | None     # where bullets go
    bullets_are_objects: bool    # True -> highlights (ID-bearing), False -> plain strings


SECTIONS = {
    "Work": SectionSpec("work", ("name", "position"), "summary", "highlights", True),
    "Volunteer": SectionSpec("volunteer", ("organization", "position"), "summary", "highlights", True),
    "Education": SectionSpec("education", ("institution", "area"), None, "courses", False),
    "Projects": SectionSpec("projects", ("name",), "description", "highlights", True),
    "Skills": SectionSpec("skills", ("name",), None, "keywords", False),
    "Awards": SectionSpec("awards", ("title",), "summary", None, False),
    "Certificates": SectionSpec("certificates", ("name",), None, None, False),
    "Publications": SectionSpec("publications", ("name",), None, None, False),
    "Languages": SectionSpec("languages", ("language",), None, None, False),
    "Interests": SectionSpec("interests", ("name",), None, "keywords", False),
    "References": SectionSpec("references", ("name",), "reference", None, False),
}
HEADING_SEP = "—"


def _split_heading(entry: Entry, spec: SectionSpec, section_title: str) -> dict:
    """Split an entry's '## ' heading into ``spec.heading_fields`` on the em dash.

    The split is bounded to ``len(spec.heading_fields) - 1`` separators, so
    only the em dashes needed to delimit fields are consumed; any further em
    dashes stay inside the last field. This matters because field values in
    the real corpus (project names, education areas) routinely contain their
    own em dashes, e.g. "lyeh-infra — Self-Hosted Kubernetes Infrastructure
    (GitOps)" as a single-field Projects heading, or "Computer Science —
    Software Architecture, Linux Kernel & DevOps" as the second half of a
    two-field Education heading.

    Residual limitation: for a two-field section, this is "first em dash
    wins" — an em dash inside the *first* field would still mis-split there.
    No entry in the corpus does that today, and escaping would cost more
    than it buys, but a future reader should know the rule.
    """
    parts = [
        p.strip()
        for p in entry.heading.split(HEADING_SEP, maxsplit=len(spec.heading_fields) - 1)
    ]
    if len(parts) != len(spec.heading_fields):
        expected = f" {HEADING_SEP} ".join(f"<{f}>" for f in spec.heading_fields)
        raise MdError(entry.line, f"'{section_title}' heading must be: {expected}")
    return dict(zip(spec.heading_fields, parts))


def _entry_to_dict(entry: Entry, spec: SectionSpec, section_title: str, key: str,
                   index: int, lines: dict) -> dict:
    out = _split_heading(entry, spec, section_title)
    lines[f"{key}[{index}]"] = entry.line

    for k, v in entry.meta.items():
        if k == "id":
            continue
        out[META_ALIASES.get(k, k)] = v

    if entry.prose:
        if spec.prose_field is None:
            raise MdError(entry.line, f"'{section_title}' entries take no prose paragraph")
        out[spec.prose_field] = entry.prose

    if entry.bullets:
        if spec.bullet_field is None:
            raise MdError(entry.line, f"'{section_title}' entries take no bullet list")
        values = []
        for n, bullet in enumerate(entry.bullets):
            if bullet.id and not spec.bullets_are_objects:
                raise MdError(bullet.line, f"'{section_title}' bullets must not carry a {{#id}}")
            values.append(bullet.text)
            lines[f"{key}[{index}].{spec.bullet_field}[{n}]"] = bullet.line
        out[spec.bullet_field] = values

    return out


def to_jsonresume(doc: Document) -> tuple[dict, dict]:
    """Return (JSON Resume data, {json path: source line})."""
    lines: dict[str, int] = {}
    basics = {k: v for k, v in doc.frontmatter.items() if k in BASICS_KEYS}
    unknown = set(doc.frontmatter) - set(BASICS_KEYS)
    if unknown:
        raise MdError(1, f"unknown frontmatter key(s): {', '.join(sorted(unknown))}")

    data: dict = {"$schema": SCHEMA_URL, "basics": basics}
    for spec in SECTIONS.values():
        data[spec.key] = []

    for section in doc.sections:
        if section.title == "Summary":
            basics["summary"] = section.prose
            lines["basics.summary"] = section.line
            continue
        spec = SECTIONS.get(section.title)
        if spec is None:
            raise MdError(section.line, f"unknown section '{section.title}'")
        data[spec.key] = [
            _entry_to_dict(e, spec, section.title, spec.key, i, lines)
            for i, e in enumerate(section.entries)
        ]

    data["meta"] = META
    return data, lines
