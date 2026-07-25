Curate the comprehensive CV (`docs/resume/cv.md`) into a JD-tailored facet resume.
Run from the lyeh-infra repo root.

**Language:** Traditional Chinese (zh-TW) for all user-facing output.

**Usage:** `/cv-tailor <a|b|c> [--jd <url-or-path>]`
- `<a|b|c>` selects the facet: A = Platform/Infrastructure/SRE · B = Data Engineer · C = MLOps/AI Platform.
- Without `--jd`: refine the tracked `docs/resume/resume-<facet>.md` (Flow 2a — write back).
- With `--jd`: produce a one-off export tailored to that specific JD (Flow 2b — **do NOT commit**, write to `/tmp/`).

`docs/resume/*.md` is the single source of truth; `docs/resume/*.json` are build artifacts
written by `make cv-build`. Never hand-edit a `.json` or a `.pdf`.

## Step 0 — Read the `cv-md` skill first (mandatory)

A facet resume is **not free-form Markdown**, and every curated bullet must carry a
provenance anchor. Before writing anything, read:

- `.claude/skills/cv-md/SKILL.md`
- `.claude/skills/cv-md/references/md-format.md` — the grammar, and §8 on bullet IDs and
  fingerprints
- `.claude/skills/cv-md/references/anti-drafting.md` — the five gates and the only honest
  ways past them

## Step 1 — Load inputs

Read, in order:
1. `docs/resume/cv.md` — the **only** source of facts. Invent nothing not derivable from it.
2. `docs/resume/rules.toml` — the machine-checked truthfulness rules (banned + qualified
   patterns). This is the authority; the prose in Step 2 is only its rationale.
3. `docs/resume/raw/resume_split_blueprint.md` — facet definitions and the human-facing
   "不可宣稱" lists. *(local-only / git-ignored; skip if absent.)*
4. `docs/resume/raw/resume_tech_gap_filling.md` — what each facet still lacks (do not claim
   gaps as proficiencies). *(local-only / git-ignored; skip if absent.)*
5. The current `docs/resume/resume-<facet>.md` — you are refining it, not rewriting it from
   scratch; keep the anchors that are already correct.
6. If `--jd` was given, read that JD (URL → fetch; path → read).

## Step 2 — Analyze and propose

Compare the facet resume against the facet spec (and the JD, if given). Produce truthful
edits only:
- the frontmatter `label` and the `# Summary` prose, angled at the facet;
- `# Work` entry bullets (→ `highlights`) reframed to the facet's foreground — same facts,
  different emphasis;
- `# Skills` entries reordered per the blueprint's facet ordering;
- `# Projects` entries selected per the blueprint;
- anything in-progress marked inline in that same bullet, e.g. `Delta Lake (learning)`,
  `GraphRAG (in-progress)`.

**Invariant fields** — the frontmatter contact block (`name`, `email`, `phone`, `location`),
every `## <employer> — <position>` heading, each Work meta block's `start` / `end` /
`location`, and the whole `# Education` and `# Languages` sections — must be **copied
verbatim from `cv.md`**, never tailored (decision #13). The Work list must also line up
positionally with the CV's.

### Every proposed facet bullet must carry a source anchor

```markdown
- Reframed version of that achievement <!-- src: csense-h3 @d85d -->
```

The hash is **exactly four lowercase hex characters**; anything else is a hard parse error.

**A bullet with no CV source is not a valid proposal.** If the facet needs a fact that
`cv.md` does not contain, the correct move is to propose adding it to `cv.md` first — and
that addition **needs the user's explicit confirmation**, because `cv.md` is their record
of their own career and only they can confirm a claim is true. Propose the wording, wait,
and only then write the CV bullet with a fresh `{#<entry-id>-h<n>}` ID and cite it here.
Never anchor a bullet to the nearest plausible-looking CV bullet to make the gate pass: a
wrong anchor is worse than a missing one, because it makes an unsupported claim look sourced.

Also: a facet bullet may **drop** a number from its source, never **introduce** one. A
merged bullet that carries numbers from two CV bullets can only cite one, and will fail —
split it, or cite the source that carries the number you kept.

### Computing `@<hash>`

The fingerprint is over the **CV** bullet's text, after `{#id}` and any `<!-- src: … -->`
have been stripped — not over your reframed facet wording, and not over the raw Markdown
line. From the repo root:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from cv_lint import cv_index, CV_MD
from resume_md import fingerprint
idx, _ = cv_index(CV_MD)
print(fingerprint(idx['csense-h3']))"
# d85d
```

Whitespace is normalised, so re-wrapping a CV line does not change its hash; a single
reworded word does. If lint reports `stale: cv.md '<id>' changed … (@old → @new)`, **re-read
the new CV text and confirm the facet wording is still true of it before** updating the
hash. Updating a hash without re-reading the source is how a false claim gets laundered
through this system.

### Truthfulness rules

These are now machine-checked against every bullet in every document by
`docs/resume/rules.toml`. The prose below is the human-facing rationale, not a second
source of truth — if the two ever disagree, `rules.toml` (and `scripts/cv_lint.py`) wins.

- MediaTek used Beam/Dataflow, **never Spark/PySpark** — `banned`.
- IaC is Helm + ArgoCD, **never Terraform** — `banned`.
- RAG / GraphRAG / LangGraph / agentic work must carry `(in-progress)`, `(learning)` or
  `(exploring)` **in the same bullet** — `qualified`.
- German must carry `beginner` or `A1`/`A2` in the same bullet — `qualified`.
- AWS = model-monitoring only, **not** platform depth. *(Not machine-checked — this one is
  still on you.)*

Never edit `rules.toml` to silence a hit. Reword the claim instead.

Present a numbered list of suggested changes (reason + proposed Markdown line, anchor
included), then **stop and wait** for the user's natural-language reply (accept all /
accept some / tweak). Mirror the `/cv-sync` approval UX.

## Step 3 — Apply

- **No `--jd`:** edit `docs/resume/resume-<facet>.md`.
- **With `--jd`:** write `/tmp/resume-<facet>-<jd-slug>.md` (ephemeral; not committed).
  Tell the user the path. Note that `make cv-build` and `make cv-render` only operate on
  `docs/resume/`, so a one-off has to be copied there to be rendered:

  ```bash
  cp /tmp/resume-a-acme.md docs/resume/     # now matches the resume-*.md glob
  make cv-render                            # runs cv-build first → docs/resume/resume-a-acme.pdf
  rm docs/resume/resume-a-acme.md docs/resume/resume-a-acme.json   # keep the PDF only
  ```

  While the copy is in `docs/resume/` it is treated as a fourth facet by `cv-build` and
  `cv-lint` (invariants, provenance, numbers and rules all apply to it). `*.pdf` is
  git-ignored; remove the `.md` and the generated `.json` again once the PDF exists.

## Step 4 — Build and check

```bash
make cv-build && make cv-lint
```

Report **both** outputs to the user.

- `make cv-build` is schema-gated and writes **nothing** for a file that fails, so a
  failing build means the JSON on disk is stale — fix the reported line in the `.md`.
- `make cv-lint` runs the five gates: invariants, provenance, numbers, banned/qualified
  terms, and generated-JSON freshness. There are pre-existing findings in this corpus that
  are content decisions for the repo owner. Do not invent anchors or reword claims you
  cannot verify to make them go away — report them and stop.

Finish with a short summary of what changed and any truthfulness guardrail you applied.
