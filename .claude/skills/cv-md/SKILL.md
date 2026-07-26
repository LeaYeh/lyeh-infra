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
                                                                             + apps/portal/src/data/resume.json
```

**Never hand-edit `docs/resume/*.json`, `docs/resume/*.pdf`, or
`apps/portal/src/data/resume.json`.** The next `make cv-build` / `make cv-publish`
overwrites them, and `make cv-lint`'s freshness and portal gates fail if they
disagree with the Markdown. If a JSON field looks wrong, the fix is in the `.md`
that produced it.

## The loop

```bash
# 1. edit the Markdown
# 2. compile it (schema-gated; writes nothing on failure)
make cv-build
# 3. run the six gates, leniently — warnings print but do not block
make cv-lint
# 4. optional — regenerate PDFs (runs cv-build + cv-lint-strict first)
make cv-render
```

`make cv-build` refuses to write any JSON whose schema validation fails, so a
broken edit never reaches the PDF or the Gist. The previous JSON stays as it was.

`make cv-lint-strict` runs the same gates with warnings promoted to blocking.
`make cv-render` and `make cv-publish` both depend on it, so nothing leaves the
working copy on a `⚠` — while plain `make cv-lint` stays lenient for iteration.
CI (`.github/workflows/resume-gates.yml`) runs the test suite and
`make cv-lint-strict` on every push and PR touching the resume set.

## Reading an error

Both tools anchor every problem to a source line:

```
✗ resume-mlops.md:46 bullet has no src anchor — add the fact to cv.md first, then cite its ID
✗ cv.md:212 RAG / LangGraph / agent work must be marked (in-progress) or framed as current activity
⚠ resume-de.md:88 stale: cv.md 'csense-h3' changed since this was written (@d85d → @1f0a); re-check the wording, then update the anchor
```

`✗` is fatal (exit 1); `⚠` is a warning (a stale anchor does not by itself fail
plain `make cv-lint`, but it does fail `make cv-lint-strict`, and therefore
blocks `cv-render` and `cv-publish`).

Findings that carry no line number name a whole file:

- the **invariants** gate names the `.md` whose fields drifted;
- the **freshness** gate names the stale `.json`;
- the **portal** gate names `apps/portal/src/data/resume.json`.

A finding on prose or frontmatter points at the prose's own line — not its
heading — and prefixes the message with which paragraph or field it is. A
frontmatter value has no line of its own, so it is anchored to line 1 and says so.

**Go to that line in that `.md` and fix the Markdown.** Never edit the generated
JSON, never edit a test expectation, never edit `rules.toml` to silence a hit.

## Which file do I edit?

| Situation | File | What you write |
|---|---|---|
| A new career fact (a real thing the human did) | `docs/resume/cv.md` | A bullet with a new `{#id}` |
| Reframing a fact that is already in the CV, for one audience | `docs/resume/resume-<facet>.md` | The reframed bullet plus `<!-- src: <cv-id> @<hash> -->` |

Facets: **swe** = Senior Software Engineer · **ai** = AI Platform / Applied AI ·
**mlops** = MLOps / DevOps / GitOps · **de** = Data Engineer.

`cv.md` is comprehensive (multi-page when rendered). `resume-swe/ai/mlops/de.md` are
one-page pitches — a curated subset, reframed to one angle, and **nothing else**.
A facet may not contain a fact the CV does not.

Contact details, profiles, homepage and avatar, employer, position, dates, work
location and URL, the whole education list and the whole languages list are
**invariants**: copied verbatim into every facet, never tailored. The invariants
gate compares them field by field.

The work lists are compared **positionally**, so a facet must carry the *same
number of work entries* as `cv.md`. To fit one page, shorten a role (its prose
and bullets are tailorable) — never delete one.

## Before you write a bullet

Read `references/anti-drafting.md`. It is short and it is the point of this
skill: the gates exist because resume drafting is where an assistant is most
tempted to smooth over a gap. The legitimate response to every gate is to change
the *claim*, never the *check*.

Note that the gates read more than bullets: entry prose, section prose and the
frontmatter `label` all reach the JSON and are all checked. Moving a
claim into a paragraph does not move it out of range.

## Bundled references

- `references/md-format.md` — the complete grammar: frontmatter keys, headings,
  `<!--meta` blocks, prose, bullets, `{#id}`, `<!-- src: id @hash -->`, the
  bullet-ID convention, and how to compute a fingerprint.
- `references/jsonresume-mapping.md` — which Markdown construct becomes which
  JSON Resume field, section by section.
- `references/anti-drafting.md` — the six gates, their exact messages, `--strict`,
  and the only acceptable fixes.

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

Report the output verbatim, including any findings you did not fix.

`make cv-lint` currently exits 1 on exactly one finding — the portal copy
(`apps/portal/src/data/resume.json`) is an older snapshot of `cv.json`, and
refreshing it means publishing, which is the repo owner's decision. **That is the
only known-and-accepted finding.** Treat every other finding as new and as yours
to fix or to report; do not assume it was already known. Never "fix" a finding by
inventing an anchor or rewording a claim you cannot verify — say what it is and
stop.
