#!/usr/bin/env python3
"""jsonresume_schema — vendored JSON Resume v1.0.0 field spec + validator.

Stdlib-only stand-in for the `jsonschema` package: it checks the field names,
types and date formats this repo actually uses, which is what the build gate needs.
"""
from __future__ import annotations

import re

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})?$")

STR, LIST_STR, DATE = "str", "list[str]", "date"

BASICS = {
    "name": STR, "label": STR, "image": STR, "email": STR, "phone": STR,
    "url": STR, "summary": STR, "location": "dict", "profiles": "list[dict]",
}
LOCATION = {"address": STR, "postalCode": STR, "city": STR, "countryCode": STR, "region": STR}
PROFILE = {"network": STR, "username": STR, "url": STR}

SECTION_FIELDS = {
    "work": ({"name": STR, "position": STR, "url": STR, "startDate": DATE,
              "endDate": DATE, "summary": STR, "highlights": LIST_STR, "location": STR},
             ("name", "position", "startDate")),
    "volunteer": ({"organization": STR, "position": STR, "url": STR, "startDate": DATE,
                   "endDate": DATE, "summary": STR, "highlights": LIST_STR},
                  ("organization", "position", "startDate")),
    "education": ({"institution": STR, "url": STR, "area": STR, "studyType": STR,
                   "startDate": DATE, "endDate": DATE, "score": STR, "courses": LIST_STR},
                  ("institution", "area")),
    "awards": ({"title": STR, "date": DATE, "awarder": STR, "summary": STR}, ("title", "date")),
    "certificates": ({"name": STR, "date": DATE, "issuer": STR, "url": STR}, ("name", "date")),
    "publications": ({"name": STR, "publisher": STR, "releaseDate": DATE, "url": STR,
                      "summary": STR}, ("name",)),
    "skills": ({"name": STR, "level": STR, "keywords": LIST_STR}, ("name",)),
    "languages": ({"language": STR, "fluency": STR}, ("language",)),
    "interests": ({"name": STR, "keywords": LIST_STR}, ("name",)),
    "references": ({"name": STR, "reference": STR}, ("name",)),
    "projects": ({"name": STR, "description": STR, "highlights": LIST_STR, "keywords": LIST_STR,
                  "startDate": DATE, "endDate": DATE, "url": STR, "roles": LIST_STR,
                  "entity": STR, "type": STR}, ("name",)),
}

Error = tuple[str, str]


def _check_value(path: str, value, kind: str) -> list[Error]:
    if kind == DATE:
        if not isinstance(value, str):
            return [(path, f"must be a string date, got {type(value).__name__}")]
        if not DATE_RE.match(value):
            return [(path, f"must be YYYY-MM-DD or empty, got '{value}'")]
        return []
    if kind == STR and not isinstance(value, str):
        return [(path, f"must be a string, got {type(value).__name__}")]
    if kind == LIST_STR:
        if not isinstance(value, list):
            return [(path, f"must be a list of strings, got {type(value).__name__}")]
        return [(f"{path}[{i}]", "must be a string")
                for i, v in enumerate(value) if not isinstance(v, str)]
    if kind == "dict" and not isinstance(value, dict):
        return [(path, f"must be a table, got {type(value).__name__}")]
    if kind == "list[dict]" and not isinstance(value, list):
        return [(path, f"must be a list of tables, got {type(value).__name__}")]
    return []


def _check_object(path: str, obj: dict, fields: dict, required: tuple = ()) -> list[Error]:
    errors: list[Error] = []
    for key in required:
        if key not in obj:
            errors.append((f"{path}.{key}", "required field is missing"))
    for key, value in obj.items():
        kind = fields.get(key)
        if kind is None:
            errors.append((f"{path}.{key}", "unknown field for this section"))
            continue
        errors.extend(_check_value(f"{path}.{key}", value, kind))
    return errors


def validate(data: dict) -> list[Error]:
    """Return a list of (json path, message). Empty means the document is valid."""
    errors: list[Error] = []
    basics = data.get("basics", {})
    errors.extend(_check_object("basics", basics, BASICS, ("name", "email")))
    if isinstance(basics.get("location"), dict):
        errors.extend(_check_object("basics.location", basics["location"], LOCATION))
    if isinstance(basics.get("profiles"), list):
        for i, p in enumerate(basics["profiles"]):
            errors.extend(_check_object(f"basics.profiles[{i}]", p, PROFILE, ("network",)))

    for key, (fields, required) in SECTION_FIELDS.items():
        entries = data.get(key, [])
        if not isinstance(entries, list):
            errors.append((key, "must be a list"))
            continue
        for i, entry in enumerate(entries):
            errors.extend(_check_object(f"{key}[{i}]", entry, fields, required))
    return errors
