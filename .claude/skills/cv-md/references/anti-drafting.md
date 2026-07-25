# Anti-drafting: the gates, and the only honest way past them

Authority: `scripts/cv_lint.py`, `scripts/cv_build.py`, `docs/resume/rules.toml`.

These gates exist because resume drafting is exactly where a language model is
most tempted to help: to round a number up, to reword a "learning X" into
"experienced with X", to attach a plausible-looking source to a sentence it
just wrote. Every gate below replaces a judgement that used to depend on an
assistant's self-restraint with something a machine checks.

**The response to a gate is always to change the claim, never the check.**

## Quick table

| Error | What it means | Legitimate fix |
|---|---|---|
| `bullet has no src anchor` | A fact exists in a facet but not in the CV | Add it to `cv.md` with a new ID, then cite that ID. Never invent an anchor. |
| `src '<id>' does not exist in cv.md` | Dangling reference | Find the real source bullet, or add the fact to `cv.md` |
| `stale: cv.md '<id>' changed` | The source was reworded | Re-read the source, confirm the facet wording is still true, then update the hash |
| `number(s) N do not appear in cv.md` | A metric was invented or altered | Use the number from the source, or add the real metric to `cv.md` with evidence |
| banned / qualified term | A claim contradicts `rules.toml` | Reword, or add the `(in-progress)` qualifier |

## Not acceptable fixes — ever

- **Updating a fingerprint without re-reading the source.** The hash exists to
  force a human-or-agent re-read. Recomputing it mechanically to make lint quiet
  converts the gate into decoration.
- **Editing `rules.toml` to silence a hit.** That file is the human's record of
  what they may not claim. Changing it to fit a draft inverts the whole design.
- **Anchoring a bullet to the nearest-looking CV bullet** so provenance passes.
  A wrong anchor is worse than a missing one: it makes an unsupported claim look
  sourced.
- **Adding a claim to `cv.md` on your own initiative so a facet can cite it.**
  This one matters most. `cv.md` is the human's record of their own career.
  Only they can confirm a claim is true. If a facet needs a fact the CV lacks,
  say so and stop — propose the wording, do not commit it.
- **Editing the generated `*.json`, the `*.pdf`, or a test expectation** to make
  a gate pass.

If you cannot fix a finding honestly, leave it and report it. A resume with a
known open finding is repairable; a resume with a false claim that passed lint
is not.

---

## Gate 0 (build) — schema conformance

`make cv-build` parses each `.md` and validates the result against the vendored
JSON Resume v1.0.0 field spec. A failure prints, per problem:

```
✗ cv.md:33 work[0].startDate: must be YYYY-MM-DD or empty, got '2024'

BUILD FAILED — no JSON was written for the files above.
```

**Nothing is written on failure.** The previous JSON stays exactly as it was, so
a broken edit never propagates to the PDF or the public Gist. That also means a
"successful-looking" render after a failed build is showing you stale output.

Legitimate fix: correct the Markdown at the reported line. See
`references/jsonresume-mapping.md` for required fields and date formats.

---

## Gate 1 — invariants

```
✗ resume-a.md 'work' drifts from cv.md — invariant fields must be copied verbatim
```

Compares `cv.md` against every `resume-*.md` on the fields that must **never** be
tailored:

- `basics`: `name`, `email`, `phone`, `location`
- each `work` entry, positionally: `name`, `position`, `startDate`, `endDate`,
  `location`
- the entire `education` array (institution, area, studyType, dates, url, score,
  courses — all of it)
- the entire `languages` array

The message names the drifting group, not the field, and carries no line number
— diff the two documents' relevant blocks.

Note what is *not* invariant, and therefore is legitimately tailorable: the
`label` in the frontmatter, the `# Summary` prose, every work `summary` and
`highlights` list, the whole Projects / Skills / Awards / Certificates /
Publications / Interests / References sections, and which work entries you
include at all — but if you include a work entry, its invariant fields must
match `cv.md` exactly, and the list must line up positionally with the CV's.

Legitimate fix: copy the field back from `cv.md` character for character. If the
CV itself is wrong, fix `cv.md` first and then re-copy into all three facets.

---

## Gate 2 — provenance

Applies to bullets in the **Work**, **Volunteer** and **Projects** sections of
every `resume-*.md`. (Education courses and Skills keywords are not curated
content and are exempt.) `cv.md` itself is not checked — it is the source.

### `bullet has no src anchor`

```
✗ resume-a.md:46 bullet has no src anchor — add the fact to cv.md first, then cite its ID
```

The bullet asserts something with no traceable origin. Either you wrote a new
fact directly into a facet, or you dropped the anchor while editing.

Legitimate fix, in order:

1. Find the CV bullet this claim came from and cite it.
2. If there is none — the fact is genuinely new — it belongs in `cv.md` first,
   as a bullet with a fresh `{#<entry-id>-h<n>}` ID. **Ask the human to confirm
   the fact before adding it.** Then cite the new ID.
3. If nobody can confirm it, delete the bullet.

### `src '<id>' does not exist in cv.md`

```
✗ resume-b.md:59 src 'mediatek-de-h9' does not exist in cv.md
```

Typo'd ID, or a CV bullet that was deleted or renamed out from under the facet.

Legitimate fix: locate the real source bullet in `cv.md` and use its actual ID
(and its actual current hash). If the source was deleted deliberately, the facet
bullet has to go too.

Related: `duplicate bullet ID '<id>'` in `cv.md` means two bullets claim the same
ID; the second is dropped from the index, so anchors silently resolve to the
first. Rename one.

### `stale: cv.md '<id>' changed`

```
⚠ resume-a.md:42 stale: cv.md 'csense-h3' changed since this was written (@d85d → @1f0a); re-check the wording, then update the anchor
```

This is a **warning** (`⚠`), not fatal — it does not by itself make `make cv-lint`
exit non-zero. That is deliberate: rewording a CV bullet should not block a
build. It is not permission to ignore it.

Legitimate fix, in this order:

1. Read the *new* CV bullet text.
2. Decide whether the facet's reframing is still a true statement of it. Often
   it is not — a softened claim in the CV must soften in the facet too.
3. Adjust the facet wording if needed.
4. **Then** update the hash to the value the message shows after the arrow, or
   recompute it (see `references/md-format.md` §8).

Doing step 4 without steps 1–3 is the single easiest way to launder a false
claim through this system.

---

## Gate 3 — numbers

```
✗ resume-a.md:74 number(s) 25 do not appear in cv.md 'mediatek-de-h3'
```

Every standalone numeric token in a facet bullet must also appear in the CV
bullet it cites. A facet may drop a number; it may never introduce one.

What counts as a number: a digit run, optionally with `.`/`,` separators and an
optional trailing `x`/`X`/`×`, that is **not** glued to a letter or digit on
either side.

- Checked: `20%` → `20`, `7.5`, `<1%` → `1`, `5x`, `25`.
- Not checked: `k3s`, `CX23`, `14K` — a digit welded to letters is an
  identifier or an abbreviation, not a measurement.
- URLs are stripped before scanning, so a digit inside a link (a doc ID, a
  query parameter) is never treated as a claim.

The blind spot is worth knowing: because `14K` is invisible to this gate, an
abbreviated metric can drift without being caught. Check those by eye.

Bullets with no resolvable `src` are skipped here — the provenance gate already
reported them.

Legitimate fix:

- Use the number exactly as the source states it, or
- Drop the number and make the claim qualitative, or
- If the real metric is different from both, correct `cv.md` — with the human's
  confirmation and whatever evidence they have — and then re-anchor.

Merging two CV bullets into one facet bullet is a common trigger: the merged
sentence carries numbers from *both* sources but can only cite one. Split it, or
cite the source that carries the number you kept.

---

## Gate 4 — banned and qualified terms

Patterns live in `docs/resume/rules.toml` and are matched case-insensitively
against **every bullet in every document, including `cv.md`**. The error text is
the rule's own `message`:

```
✗ cv.md:44 RAG / LangGraph / agent work must be marked (in-progress)
✗ cv.md:460 RAG / LangGraph / agent work must be marked (in-progress)
```

Two rule kinds:

- **`banned`** — the pattern may not appear at all. Currently: `spark`/`pyspark`
  (the MediaTek work used Beam/Dataflow, never Spark) and `terraform` (IaC here
  is Helm + ArgoCD).
- **`qualified`** — the pattern may appear only if a second pattern appears in
  the *same bullet*. Currently: `rag`/`graphrag`/`langgraph`/`agentic` require
  `(in-progress)`, `(learning)` or `(exploring)` in parentheses; `german`
  requires `beginner` or `a1`/`a2`.

The qualifier must be in the same bullet — a nearby bullet, the entry prose, or
the summary does not satisfy it.

Legitimate fix: reword the claim so the banned term is not needed (name the tool
actually used), or add the required qualifier to that bullet.

Not legitimate: relaxing the regex, deleting the rule, or moving the claim into
prose where the gate does not look. Prose is not scanned — that is a limitation
of the gate, not a loophole to use.

---

## Gate 5 — generated-JSON freshness

```
✗ resume-c.json is out of date with the Markdown — run `make cv-build`
✗ resume-c.json missing — run `make cv-build`
```

The committed `.json` must equal what the `.md` builds to right now. This is what
stops a hand-edit of the JSON from surviving: the next lint reports it, and the
next build erases it.

Legitimate fix: `make cv-build`. If the resulting JSON is not what you wanted,
the change belongs in the `.md`.

---

## The invariant rule, stated plainly

Contact details, employer, position, dates, work location, education and
languages are **copied verbatim across all four documents** — `cv.md`,
`resume-a.md`, `resume-b.md`, `resume-c.md` — and are never tailored per facet.

Tailoring means choosing *which* true facts to show and *how to frame* them for
one audience. It does not mean changing what the facts are. A job title that
shifts between facets, or an end date that moves to close a gap, is not
tailoring — it is fabrication, and Gate 1 exists to catch it.
