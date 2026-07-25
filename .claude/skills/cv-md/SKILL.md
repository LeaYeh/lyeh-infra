---
name: cv-md
description: Edit the Markdown resume SSOT (docs/resume/*.md) — format rules, the build/lint gates, and what must never be invented. Use when editing, reviewing, or generating any resume content in lyeh-infra.
---

# cv-md — editing the Markdown resume SSOT

## The one rule that governs everything

`docs/resume/*.md` is the single source of truth. Everything else is a build artifact:

```
docs/resume/*.md  --make cv-build-->  docs/resume/*.json  --make cv-render-->  *.pdf
                                                          --make cv-publish--> public Gist
```

**Never hand-edit `docs/resume/*.json` or `docs/resume/*.pdf`.** The next
`make cv-build` overwrites them, and `make cv-lint`'s freshness gate fails if
they disagree with the Markdown. If a JSON field looks wrong, the fix is in the
`.md` that produced it.

## The loop

```bash
# 1. edit the Markdown
# 2. compile it (schema-gated; writes nothing on failure)
make cv-build
# 3. run the five gates
make cv-lint
# 4. optional — regenerate PDFs (runs cv-build first)
make cv-render
```

`make cv-build` refuses to write any JSON whose schema validation fails, so a
broken edit never reaches the PDF or the Gist. The previous JSON stays as it was.

## Reading an error

Both tools anchor every problem to a source line:

```
✗ resume-a.md:46 bullet has no src anchor — add the fact to cv.md first, then cite its ID
✗ cv.md:44 RAG / LangGraph / agent work must be marked (in-progress)
⚠ resume-b.md:88 stale: cv.md 'csense-h3' changed since this was written (@d85d → @1f0a); ...
```

`✗` is fatal (exit 1); `⚠` is a warning (a stale anchor does not by itself fail
lint). A few lint findings carry no line and name the `.json` instead — those
come from the invariants and freshness gates, which compare whole documents.

**Go to that line in that `.md` and fix the Markdown.** Never edit the generated
JSON, never edit a test expectation, never edit `rules.toml` to silence a hit.

## Which file do I edit?

| Situation | File | What you write |
|---|---|---|
| A new career fact (a real thing the human did) | `docs/resume/cv.md` | A bullet with a new `{#id}` |
| Reframing a fact that is already in the CV, for one audience | `docs/resume/resume-<facet>.md` | The reframed bullet plus `<!-- src: <cv-id> @<hash> -->` |

Facets: **a** = Platform / Infrastructure / SRE · **b** = Data Engineer ·
**c** = MLOps / AI Platform.

`cv.md` is comprehensive (multi-page when rendered). `resume-a/b/c.md` are
one-page pitches — a curated subset, reframed to one angle, and **nothing else**.
A facet may not contain a fact the CV does not.

Contact details, employer, position, dates, work location, the whole education
list and the whole languages list are **invariants**: copied verbatim into every
facet, never tailored. The invariants gate compares them field by field.

## Before you write a bullet

Read `references/anti-drafting.md`. It is short and it is the point of this
skill: the gates exist because resume drafting is where an assistant is most
tempted to smooth over a gap. The legitimate response to every gate is to change
the *claim*, never the *check*.

## Bundled references

- `references/md-format.md` — the complete grammar: frontmatter keys, headings,
  `<!--meta` blocks, prose, bullets, `{#id}`, `<!-- src: id @hash -->`, the
  bullet-ID convention, and how to compute a fingerprint.
- `references/jsonresume-mapping.md` — which Markdown construct becomes which
  JSON Resume field, section by section.
- `references/anti-drafting.md` — the five gates, their exact messages, and the
  only acceptable fixes.

## Bundled templates

- `templates/cv.md` — every section in document order with one placeholder entry
  each, showing the meta keys that section accepts.
- `templates/resume-facet.md` — the one-page shape with anchored bullets.

Copy a template, replace the placeholders, then build. Do not copy real career
content out of these templates — they are deliberately generic.

## Finish every edit with

```bash
make cv-build && make cv-lint
```

Report the output verbatim, including any findings you did not fix. There are
pre-existing findings in the real corpus that are content decisions for the
repo owner — do not "fix" them by inventing anchors or rewording claims you
cannot verify. Say what they are and stop.
