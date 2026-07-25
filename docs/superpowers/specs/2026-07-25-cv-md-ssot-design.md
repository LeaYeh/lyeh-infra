# Markdown as Resume SSOT — Design

**Date:** 2026-07-25
**Status:** Approved

## Goal

Neither `cv.json` nor the rendered PDF is a workable medium for human review and
editing. Promote Markdown to the single source of truth for the whole resume set,
generate JSON Resume from it, and make the properties that used to depend on agent
discipline — schema conformance, cv↔resume synchronisation, factual grounding —
enforced by deterministic scripts instead.

## Scope

All four resume documents become Markdown SSOT:

| SSOT (hand-edited) | Generated (committed build artifact) |
|---|---|
| `docs/resume/cv.md` | `docs/resume/cv.json` |
| `docs/resume/resume-a.md` | `docs/resume/resume-a.json` |
| `docs/resume/resume-b.md` | `docs/resume/resume-b.json` |
| `docs/resume/resume-c.md` | `docs/resume/resume-c.json` |

Facet resumes are derived from `cv.md` by `/cv-tailor`, but once a human edits
`resume-<facet>.md` that file is authoritative for that facet.

## Data flow

```
docs/resume/*.md  ──make cv-build──▶  docs/resume/*.json  ──make cv-render──▶ *.pdf
   ▲ SSOT (hand-edited)                  ▲ generated       ──make cv-publish──▶ Gist
   │
   ├── /cv-sync    portal/blog ──▶ cv.md
   └── /cv-tailor  cv.md ──▶ resume-{a,b,c}.md
```

`scripts/cv_render.py`, `make cv-render` and `make cv-publish` are unchanged — they
consume JSON, which is now a build product.

## Markdown format

Prose (summaries, highlights) stays plain Markdown; structured fields live in TOML
carried by frontmatter and HTML-comment meta blocks, so they are invisible when the
document is rendered.

TOML is chosen over YAML because `tomllib` is in the Python 3.14 standard library —
the repo's scripts are stdlib-only — and it reports parse failures with line numbers
rather than requiring a hand-rolled subset parser that guesses.

```markdown
+++
name = "Lea (Mei Ling) Yeh"
label = "Senior Software Engineer | Systems Architecture"
email = "lea.yeh.ml@gmail.com"
phone = ""
image = "https://gravatar.com/avatar/..."

[location]
city = "Vienna"
countryCode = "AT"
address = "Austria, Vienna"
postalCode = "1190"

[[profiles]]
network = "LinkedIn"
username = "Lea Yeh"
url = "https://www.linkedin.com/in/lea-yeh-60296b74/"
+++

# Summary

Senior Software Engineer and de facto systems architect at c-sense...

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
end = ""
location = "Vienna, Austria"
url = "https://www.c-sense.at/"
-->

c-sense develops nanoscale sensor technology and AFM/SPM instrumentation...

- Driving the company's AI integration initiative as sole tech lead... {#csense-h1}
- Cut CI feedback loop from 20 min to 4 min... {#csense-h2}
```

Rules:

- The `## <name> — <position>` heading supplies `work[].name` and `work[].position`.
- The meta block supplies the remaining structured fields. `id` is mandatory and
  must be unique across the document.
- The first paragraph after the meta block is `work[].summary`; the bullet list is
  `work[].highlights`.
- Sections map by `# <Section>` heading: Summary, Work, Volunteer, Education,
  Projects, Skills, Awards, Certificates, Languages, Interests.

Every section uses the same shape — `##` heading, optional meta block, optional
prose paragraph, optional bullet list — so there is one grammar to learn and one
parser to maintain. Sections whose JSON Resume entries carry no prose degenerate to
a heading plus a meta block, or to a bullet list where the bullets *are* the data:

```markdown
# Skills

## Platform & Infrastructure
<!--meta
level = "Advanced"
-->

- Kubernetes
- ArgoCD
- Helm

# Languages

## Chinese
<!--meta
fluency = "Native speaker"
-->

## German
<!--meta
fluency = "Beginner"
-->
```

Under Skills the bullets become `keywords`; under Education they become `courses`.
Which sections treat bullets as `highlights` vs. a named string array is fixed by a
table in `references/jsonresume-mapping.md` and encoded in the parser — it is not
inferred. Bullets that map to a plain string array (keywords, courses) carry no
`{#id}`; only `highlights` bullets are ID-bearing, because only those are curated
into facet resumes.

## Provenance

- **Bullet IDs are non-positional.** `{#csense-h2}` derives its prefix from the
  entry's `id`, so reordering entries does not invalidate references. IDs must be
  unique document-wide; lint enforces this.
- **Facet bullets cite their source with a content fingerprint.**
  `<!-- src: csense-h2 @4f2a -->` where `4f2a` is the first 4 hex characters of the
  SHA-256 of the cv bullet text at the time it was copied.
- **Downstream sync detection:** if the cv bullet is later edited, the fingerprint
  no longer matches and lint reports `stale`.
- **Upstream sync enforcement:** a facet bullet with no `src` anchor is treated as
  fabricated and fails lint. New facts must be added to `cv.md` first, where they
  get an ID.

## Gates

All three gates run in deterministic scripts. None depend on agent self-restraint.

| Gate | Implemented in | Failure behaviour |
|---|---|---|
| Schema | `scripts/cv_md.py` | After MD→JSON, validate against a vendored JSON Resume field spec (allowed keys, types, `YYYY-MM-DD` dates). Any violation: refuse to write the JSON, leave the previous version intact, report the offending MD line. |
| Provenance | `scripts/cv-lint.py` | Missing `src`, or `src` pointing at a nonexistent ID → fail. Fingerprint mismatch → `stale` warning. |
| Numbers & banned terms | `scripts/cv-lint.py` | Every digit sequence in a facet bullet must appear in its source cv bullet. Banned-term regexes → fail. |

The parser maintains a `JSON path → MD line number` map so every error points back
to e.g. `cv.md:41`.

### New file: `docs/resume/rules.toml`

The truthfulness rules currently live in `raw/resume_split_blueprint.md`, which is
git-ignored — lint cannot read it. Move the machine-checkable subset into a
committed `docs/resume/rules.toml`: banned patterns (`Spark`, `PySpark`,
`Terraform`), and terms requiring a qualifier (RAG / LangGraph / GraphRAG must carry
`(in-progress)`). The prose blueprint remains the human-facing rationale.

## Skill bundle

```
.claude/skills/cv-md/
├── SKILL.md                      # workflow: edit MD → cv-build → cv-lint → cv-render
├── references/
│   ├── md-format.md              # full grammar: frontmatter, meta blocks, IDs, src anchors
│   ├── anti-drafting.md          # what each gate blocks and the legitimate way to fix it
│   └── jsonresume-mapping.md     # MD construct → JSON Resume field table
└── templates/
    ├── cv.md                     # full CV skeleton with per-section comments
    └── resume-facet.md           # one-page facet skeleton demonstrating src anchors
```

## Agent write policy

Agents may write the Markdown files directly — human review happens on the Markdown
file itself via `git diff`, not through a numbered approval list in conversation.
After any write, the agent must run `make cv-build && make cv-lint` and report the
result. The gates, not an approval prompt, are what prevent fabrication.

Invariant fields (contact, employer, position, dates, location, education,
languages) remain off-limits to agents and are cross-checked by lint across all four
Markdown files.

## Impact on existing tooling

- **New:** `scripts/cv_md.py` (parser + schema gate), `make cv-build`.
- **Changed:** `scripts/cv-lint.py` — invariants read from Markdown; adds
  provenance, numbers, banned-term, and generated-JSON-freshness checks.
- **Changed:** `.claude/commands/cv-sync.md` and `cv-tailor.md` — target `.md`
  files, and must emit `src` anchors (facets) and source citations (cv).
- **Changed:** `make cv-lint` and `make cv-render` run `cv-build` first.
- **Unchanged:** `scripts/cv_render.py`, `make cv-publish`.
- **Docs:** `docs/resume/README.md` and the root `CLAUDE.md` resume section.

## Migration

One-off conversion of the four existing JSON files to Markdown. Acceptance
criterion: building the Markdown back to JSON produces a field-level diff of zero
against the original JSON (ordering and formatting normalised).

## Testing

Extends `scripts/tests/`, following the existing pytest layout, TDD per component:

- Parser: frontmatter, meta blocks, heading→field mapping, line-number mapping.
- Schema gate: bad date format, unknown key, wrong type — each must refuse to write
  and name the correct MD line.
- Provenance: missing anchor, dangling ID, stale fingerprint.
- Numbers: a digit present in a facet bullet but absent from its source fails.
- Banned terms: each rule in `rules.toml` triggers.
- Round-trip: fixture MD → JSON → expected JSON.

## Rejected alternatives

- **MD as a one-way review sheet** (JSON stays SSOT): edits still funnel through an
  agent, which is the exact failure mode being designed out.
- **MD↔JSON round-trip with JSON as SSOT**: two editable representations of the same
  data, guaranteed to diverge.
- **Similarity-based sync without IDs**: facet bullets legitimately reword the source,
  so similarity scoring produces false positives and cannot be a hard gate.
- **YAML frontmatter via PyYAML**: adds a dependency to a stdlib-only script set.
- **Agent-mediated reconciliation** (`/cv-reconcile`): puts synchronisation back
  under agent judgement.
