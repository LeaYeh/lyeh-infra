# cv-sync Design

**Date:** 2026-06-16  
**Status:** Approved

## Problem

CV and resume are maintained separately (JSON Resume on GitHub Gist, visual resume on Canva). When portal content is updated (posts, projects, about), there is no prompt to keep the CV in sync.

## Goal

A manual command (`make cv-sync`) that reads all portal content, compares it against the current JSON Resume, and interactively suggests updates — applying confirmed changes directly to the gist.

## Scope

- **In scope:** `content/posts/`, `content/projects/`, `content/about.md`
- **In scope:** JSON Resume on GitHub Gist (read + write via API)
- **Partial scope:** Canva resume — output text suggestions only, no API automation (Canva has no public edit API)
- **Out of scope:** Auto-triggering on commit or file save

## Architecture

```
make cv-sync
    └── scripts/cv-sync.py
            ├── 1. Read all content/ markdown files
            ├── 2. Fetch JSON Resume from GitHub Gist API
            ├── 3. Call Claude API — compare portal vs CV, return suggestions as JSON array
            ├── 4. Interactive loop: present each suggestion, user accepts/skips/edits
            ├── 5. Merge accepted patches into JSON Resume
            ├── 6. Update gist via GitHub Gist API
            └── 7. Print Canva suggestion summary (manual action required)
```

## File Layout

```
scripts/cv-sync.py      # main script
scripts/cv-sync.env     # GIST_ID=xxx (gitignored, never committed)
Makefile                # cv-sync target
```

## Environment Variables

| Variable            | Source        | Notes                              |
|---------------------|---------------|------------------------------------|
| `ANTHROPIC_API_KEY` | existing      | reuse from current env             |
| `GITHUB_TOKEN`      | existing/new  | must have `gist` write scope       |
| `GIST_ID`           | cv-sync.env   | ID of the JSON Resume gist         |

## Claude API Call

Single call per run. Prompt includes:
1. All `content/` markdown (estimated 3–5k tokens)
2. Current JSON Resume (full JSON)
3. Instruction: identify missing or outdated information; return a JSON array where each item has:
   - `field` — dot-path to the CV field (e.g. `work[0].highlights`)
   - `reason` — why this change is suggested
   - `patch` — suggested value or append item

## Interactive UX

```
[1/4] work[0].highlights — new item suggested
      Reason: AI integration initiative added to about.md, not reflected in CV
      Patch: "Led end-to-end internal AI automation pipeline..."
      → [y] accept / [n] skip / [e] edit manually: _

...

✓ Gist updated (3 of 4 suggestions accepted).

📋 Canva suggestions (manual):
  - Summary: add AI initiative paragraph
  - Skills section: add RAG Pipelines, Structured Information Extraction
```

## Constraints

- Canva cannot be automated (no public content-editing API); output is advisory text only.
- `scripts/cv-sync.env` must be added to `.gitignore`.
- Script uses `uv run` for Python dependency management, consistent with repo tooling.

## Dependencies

- `anthropic` Python SDK
- `requests` (GitHub Gist API calls)
- Python 3.11+
