#!/usr/bin/env python3
"""cv-lint — drift backstop for the resume SSOT (decision #13).

cv.json is the source of invariant truth. Every resume-*.json must agree with it on
fields that are NOT supposed to be tailored: contact basics + each work entry's
employer/position/dates/location, plus education and languages.

Exit non-zero if any tailored resume drifts from cv.json on those invariants.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RESUME_DIR = Path(__file__).resolve().parent.parent / "docs" / "resume"
CV = RESUME_DIR / "cv.json"

# Fields that must be identical across cv.json and every resume-*.json.
BASICS_KEYS = ("name", "email", "phone", "location")
WORK_KEYS = ("name", "position", "startDate", "endDate", "location")


def load(p: Path) -> dict:
    with p.open() as f:
        return json.load(f)


def invariants(d: dict) -> dict:
    return {
        "basics": {k: d.get("basics", {}).get(k) for k in BASICS_KEYS},
        "work": [tuple(w.get(k) for k in WORK_KEYS) for w in d.get("work", [])],
        "education": d.get("education"),
        "languages": d.get("languages"),
    }


def main() -> int:
    if not CV.exists():
        print(f"✗ {CV} not found", file=sys.stderr)
        return 2
    ref = invariants(load(CV))
    resumes = sorted(RESUME_DIR.glob("resume-*.json"))
    if not resumes:
        print("No resume-*.json files to check.")
        return 0

    drift = False
    for r in resumes:
        cur = invariants(load(r))
        for section in ("basics", "work", "education", "languages"):
            if cur[section] != ref[section]:
                drift = True
                print(f"✗ {r.name}: '{section}' drifts from cv.json")
                if section == "work":
                    for a, b in zip(cur["work"], ref["work"]):
                        if a != b:
                            print(f"    cv.json : {b}")
                            print(f"    {r.name}: {a}")
    if drift:
        print("\nDRIFT DETECTED — invariant fields must be re-copied from cv.json.")
        return 1
    print(f"✓ invariants consistent across cv.json + {len(resumes)} resume(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
