# Anti-drafting: the gates, and the only honest way past them

Authority: `scripts/cv_lint.py`, `scripts/cv_build.py`, `docs/resume/rules.toml`.

These gates exist because resume drafting is exactly where a language model is
most tempted to help: to round a number up, to reword a "learning X" into
"experienced with X", to attach a plausible-looking source to a sentence it
just wrote. Every gate below replaces a judgement that used to depend on an
assistant's self-restraint with something a machine checks.

**The response to a gate is always to change the claim, never the check.**

## Bullets are not the document

About half of what reaches the JSON is not a bullet. The `# Summary` prose
becomes `basics.summary`; an entry's prose becomes `work[].summary` /
`projects[].description`; the frontmatter `label` becomes `basics.label`, the
first line a reader sees. **The rules and numbers gates read all of it** —
frontmatter `label`, section prose, entry prose and bullets alike.
Moving a claim out of a bullet and into a paragraph does not move it out of
range.

## Quick table

| Error | What it means | Legitimate fix |
|---|---|---|
| `bullet has no src anchor` | A fact exists in a facet but not in the CV | Add it to `cv.md` with a new ID, then cite that ID. Never invent an anchor. |
| `src '<id>' does not exist in cv.md` | Dangling reference | Find the real source bullet, or add the fact to `cv.md` |
| `src '<id>' belongs to entry '<x>', not '<y>'` | A claim was moved to an employer that did not earn it | Move the bullet back, or cite a bullet from the entry it now sits in |
| `stale: cv.md '<id>' changed` | The source was reworded | Re-read the source, confirm the facet wording is still true, then update the hash |
| `number(s) N do not appear in …` | A metric was invented or altered | Use the number from the source, or add the real metric to `cv.md` with evidence |
| `'<word>' has no counterpart in …` | A spelled-out magnitude ("doubled") is ungrounded | Check it by eye; reword to the real figure or drop the claim |
| banned / qualified term | A claim contradicts `rules.toml` | Reword, or add the qualifier the rule requires |
| `… is out of date with the Markdown` | The committed JSON no longer matches its `.md` | `make cv-build` |
| `apps/portal/src/data/resume.json is out of date` | The portal's published copy is behind `cv.json` | `make cv-publish` — never hand-edit the copy |

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
- **Moving a claim from a bullet into prose or the frontmatter `label`** to get
  around a rule. All four are checked; this is not a loophole, and attempting it
  is worse than the original claim.
- **Editing the generated `*.json`, the `*.pdf`, the portal copy, or a test
  expectation** to make a gate pass.

If you cannot fix a finding honestly, leave it and report it — but report it as
*your* finding, not as someone else's known issue. Do not assume any finding you
see was already known and accepted. A resume with an open finding you named is
repairable; a resume with a false claim that passed lint is not.

## Two severities, and `--strict`

`✗` is fatal — `make cv-lint` exits 1. `⚠` is a warning: it prints, and plain
`make cv-lint` still exits 0, so ordinary iteration is not blocked by (say) a
stale anchor left behind by a reworded CV bullet.

`make cv-lint-strict` runs the same gates with `--strict`, which promotes every
warning to blocking:

```
✗ --strict: 3 warning(s) block a publishing path — resolve them, or run `make cv-lint` while you iterate
```

**`make cv-render` and `make cv-publish` both depend on `cv-lint-strict`.**
Nothing that leaves the working copy — a PDF, the Gist, the portal copy — may
ship on a `⚠`. `.github/workflows/resume-gates.yml` runs the test suite and
`make cv-lint-strict` on every push and PR touching `docs/resume/**`,
`scripts/**`, `Makefile` or the portal copy.

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
✗ resume-mlops.md 'work' drifts from cv.md — invariant fields must be copied verbatim
```

Compares `cv.md` against every `resume-*.md` on the fields that must **never** be
tailored:

- `basics`: `name`, `email`, `phone`, `location`, `profiles`, `url`, `image`
- each `work` entry, positionally: `name`, `position`, `startDate`, `endDate`,
  `location`, `url`
- the entire `education` array (institution, area, studyType, dates, url, score,
  courses — all of it)
- the entire `languages` array

Contact is the obvious half. `profiles`, `url` and `image` are the other half:
they are *attribution*, and a facet that quietly points its LinkedIn, homepage
or avatar somewhere else is claiming a different person's identity just as
effectively as a changed email.

The message names the drifting group, not the field, and carries no line number
— it names the **`.md`**, so diff the two documents' relevant blocks.

### A facet may not drop a work entry

The `work` lists are compared **positionally, as whole lists**. A facet with
three work entries against a CV with four is a `'work' drifts` failure, even if
all three match. Compressing to one page by deleting the oldest job — the most
natural move there is — does not work here. Shorten a role instead: its prose
and its `highlights` are fully tailorable, so an entry can be reduced to its
heading, its meta block and a single bullet.

Note what is *not* invariant, and therefore is legitimately tailorable: the
`label` in the frontmatter, the `# Summary` prose, every work `summary` and
`highlights` list, and the whole Projects / Skills / Awards / Certificates /
Publications / Interests / References sections. The rules and numbers gates
police those instead.

Legitimate fix: copy the field back from `cv.md` character for character. If the
CV itself is wrong, fix `cv.md` first and then re-copy into all three facets.

---

## Gate 2 — provenance

Applies to bullets in the **Work**, **Volunteer** and **Projects** sections of
every `resume-*.md`. (Education courses and Skills keywords are not curated
content and are exempt.) `cv.md` itself is not checked — it is the source. Prose
carries no anchor and is not checked here either; the numbers gate grounds it by
entry `id` instead.

### `bullet has no src anchor`

```
✗ resume-mlops.md:46 bullet has no src anchor — add the fact to cv.md first, then cite its ID
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
✗ resume-de.md:59 src 'mediatek-de-h9' does not exist in cv.md
```

Typo'd ID, or a CV bullet that was deleted or renamed out from under the facet.

Legitimate fix: locate the real source bullet in `cv.md` and use its actual ID
(and its actual current hash). If the source was deleted deliberately, the facet
bullet has to go too.

Related: `duplicate bullet ID '<id>'` in `cv.md` means two bullets claim the same
ID; the second is dropped from the index, so anchors silently resolve to the
first. Rename one.

### `src '<id>' belongs to entry '<x>', not '<y>'`

```
✗ resume-mlops.md:23 src 'beta-h1' belongs to entry 'beta', not 'acme' — cite a bullet from this entry, or move the claim to the entry that earned it
```

A live anchor with a current fingerprint proves the cited sentence still exists
and still reads the way it did. It says nothing about whether it belongs *here*.
Moving a MediaTek achievement under the c-sense entry, anchor and all, is exactly
what an assistant reshuffling a facet does — so the cited bullet must also be
owned by the entry the citing bullet sits in. Ownership is read off the `cv.md`
tree, not parsed out of the ID.

Legitimate fix: put the claim back under the employer that earned it, or cite a
bullet that entry actually owns. Never re-point the anchor at a nearby ID from
the right entry to make the message go away — that is the "wrong anchor" failure
in a new costume.

### `stale: cv.md '<id>' changed`

```
⚠ resume-mlops.md:22 stale: cv.md 'acme-h1' changed since this was written (@ffff → @e673); re-check the wording, then update the anchor
```

This is a **warning** (`⚠`), not fatal — it does not by itself make `make cv-lint`
exit non-zero. That is deliberate: rewording a CV bullet should not block ordinary
editing. It **does** block `make cv-render` and `make cv-publish`, which run
`cv-lint-strict`. It is not permission to ignore it.

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

Only `resume-*.md` are checked: `cv.md` has nothing above it to be grounded
against. Every checkable string in a facet is grounded against a specific piece
of `cv.md`:

| Facet text | Grounded against | Message says |
|---|---|---|
| a bullet | the `cv.md` bullet its `src` cites | `cv.md '<bullet-id>'` |
| entry prose | the `cv.md` entry with the same meta `id` — its prose and all its bullets | `cv.md entry '<entry-id>'` |
| section prose (e.g. `# Summary`) | the whole of `cv.md` | `cv.md` |
| frontmatter `label` | the whole of `cv.md` | `cv.md` |

```
✗ resume-mlops.md:22 number(s) 40 do not appear in cv.md 'acme-h1'
✗ resume-mlops.md:20 'Acme — Engineer' prose: number(s) 200ms do not appear in cv.md entry 'acme'
✗ resume-mlops.md:9 'Summary' prose: number(s) 14K do not appear in cv.md
```

A facet may drop a number; it may never introduce one. Comparison is
case-insensitive (`14K` and `14k` are the same claim) while the message keeps the
spelling the facet used.

### What counts as a number

A digit run, optionally with `.`/`,` separators, that is **not** preceded by a
letter or digit. A short letter run *after* it stays inside the token, so the
token carries its unit.

- Checked: `20%` → `20`, `7.5`, `<1%` → `1`, `5x`, `25`, and — the ones a bare
  trailing-letter veto used to hide — `200ms`, `30TB`, `4GB`, `3rd`, `14K`.
- Not checked: `k3s`, `CX23`, `Python3`, `v1` — a digit *preceded* by a letter
  or digit is an identifier, not a measurement. Nor `3D`: a single non-magnitude
  letter is not a unit, so the trailing run must be at least two letters unless
  it is `K`/`M`/`B` or `x`/`×`.
- URLs are stripped before scanning, so a digit inside a link (a doc ID, a
  query parameter) is never treated as a claim.

### Spelled-out magnitudes — a warning, not a block

```
⚠ resume-mlops.md:1 frontmatter 'label' (no line of its own; anchored to line 1): 'doubled' has no counterpart in cv.md — a spelled-out magnitude cannot be checked mechanically; verify by eye
```

`doubled`, `halved`, `tripled`, `quadrupled`, `thousand`, `million`, `billion`,
`twofold`, `threefold` and `order of magnitude` are claims with no digit in them.
If the word is absent from the grounding text, you get a `⚠` naming the phrase to
check by eye. Non-fatal for `make cv-lint`; blocking for `cv-lint-strict`, so it
must be resolved before anything ships.

### Where findings point

A bullet finding points at the bullet's line. A prose finding points at **the
prose's own line**, not at the heading above it, and prefixes the message with
which paragraph it is. A frontmatter value has no line of its own — the parser
hands back a TOML dict, not a position — so it is anchored to line 1 and the
message says so, rather than let you read line 1 as a real location.

Bullets with no resolvable `src` are skipped here — the provenance gate already
reported them, and one defect should not be reported twice.

### Legitimate fix

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
against **every published string in every document, including `cv.md`** —
bullets, entry prose, section prose, and the frontmatter `label`. The
error text is the rule's own `message`, prefixed for non-bullet text with where
it came from:

```
✗ cv.md:212 RAG / LangGraph / agent work must be marked (in-progress) or framed as current activity
✗ resume-mlops.md:9 'Summary' prose: IaC here is Kustomize + ArgoCD, never Terraform/OpenTofu/Terragrunt
```

Two rule kinds:

- **`banned`** — the pattern may not appear at all, and no qualifier rescues it.
- **`qualified`** — the pattern may appear only if the rule's `requires` pattern
  also matches the **same string**. A qualifier in a neighbouring bullet, in the
  entry prose, or in the summary does not satisfy it.

`rules.toml` is the authority; read it. As of today it holds:

| Kind | Matches | Needs / why |
|---|---|---|
| banned | `spark`, `pyspark` | MediaTek used Beam/Dataflow, never Spark |
| banned | `terraform`, `opentofu`, `terragrunt` | **IaC here is Kustomize-organised manifests reconciled by ArgoCD** |
| banned | `ec2`, `eks`, `ecs`, `rds`, `vpc`, `redshift`, `athena`, `sagemaker`, `dynamodb`, `cloudformation`, `fargate`, `cloudwatch`, `kinesis`, `aws lambda`, `aws glue` | S3 was the only AWS service ever used |
| qualified | `rag`, `graphrag`, `langgraph`, `agentic`, `retrieval-augmented generation` (hyphen or space), `langchain`, `llamaindex`, `agent`/`agents`/`multi-agent` | needs `(in-progress)`, `(learning)` or `(exploring)`, **or** present-continuous framing: `currently <verb>ing …` / `evaluating …` |
| qualified | `databricks` | needs `certified` / `certificate` / `certification` |
| qualified | `german` | needs `beginner` or `a1`/`a2` |
| qualified | `aws` | needs `monitor…` — AWS work was model monitoring, not platform depth |

The parenthesised marker and the present-continuous framing are equally
acceptable to the gate, but they are not equally strict: `currently architecting`
matches anywhere in the string, so it can satisfy the rule for a term it does not
actually qualify. **When a sentence could read as a proficiency claim, use the
`(in-progress)` marker.**

### The IaC rule, spelled out

This repository's infrastructure is **Kustomize** overlays (`kustomization.yaml`
under `apps/` and `argocd/install/`) reconciled by **ArgoCD**. There is no
`Chart.yaml` and nothing invokes `helm`. When you reword a Terraform claim, name
what is actually used — Kustomize and ArgoCD. Do **not** write "Helm": it is not
what runs here, `helm` has no rule in `rules.toml`, and a false Helm bullet
therefore passes every gate in this document.

Legitimate fix: reword the claim so the banned term is not needed (naming the
tool actually used), or add the qualifier the rule requires to that same string.

Not legitimate: relaxing the regex, deleting the rule, or moving the claim into
prose or the frontmatter — prose and frontmatter are scanned too.

---

## Gate 5 — generated-JSON freshness

```
✗ resume-mlops.json is out of date with the Markdown — run `make cv-build`
✗ resume-mlops.json missing — run `make cv-build`
```

The committed `.json` must equal what the `.md` builds to right now. This is what
stops a hand-edit of the JSON from surviving: the next lint reports it, and the
next build erases it. These findings name the **`.json`** and carry no line
number.

Legitimate fix: `make cv-build`. If the resulting JSON is not what you wanted,
the change belongs in the `.md`.

---

## Gate 6 — the portal copy

```
✗ apps/portal/src/data/resume.json is out of date with docs/resume/cv.json — run `make cv-publish` to refresh it (never hand-edit the portal copy)
⚠ apps/portal/src/data/resume.json not found — this clone has no portal copy to check
```

`apps/portal/src/data/resume.json` is a **third public surface**, alongside the
PDF and the Gist: it is tracked, and `.github/workflows/portal-deploy.yml`
deploys on any push under `apps/portal/src/**`. `make cv-publish` writes it as
its last step. This gate requires it to equal what `cv.md` builds to.

A missing file is a `⚠` — this repo can legitimately be cloned without
`apps/portal` — while a stale one is fatal.

Legitimate fix: `make cv-publish`. Never hand-edit the copy; it is an artifact of
`cv.md` like every other JSON here.

> **The one finding open in this repo today is this gate.** The committed portal
> copy is an older snapshot, and refreshing it means publishing — a decision for
> the repo owner, not for an assistant. So `make cv-lint` currently exits 1 with
> exactly this one line and nothing else. Anything *else* you see is new, and is
> yours to report.

---

## The invariant rule, stated plainly

Contact details, profiles, homepage and avatar, employer, position, dates, work
location, work URL, education and languages are **copied verbatim across all four
documents** — `cv.md`, `resume-mlops.md`, `resume-de.md`, `resume-mlops.md` — and are
never tailored per facet.

Tailoring means choosing *which* true facts to show and *how to frame* them for
one audience. It does not mean changing what the facts are, and it does not mean
dropping a job. A job title that shifts between facets, or an end date that moves
to close a gap, is not tailoring — it is fabrication, and Gate 1 exists to catch it.
