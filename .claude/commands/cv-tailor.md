Curate the comprehensive CV (`docs/resume/cv.json`) into a JD-tailored facet resume.
Run from the lyeh-infra repo root.

**Language:** Traditional Chinese (zh-TW) for all user-facing output.

**Usage:** `/cv-tailor <a|b|c> [--jd <url-or-path>]`
- `<a|b|c>` selects the facet: A = Platform/Infrastructure · B = Data Engineer · C = MLOps/AI Platform.
- Without `--jd`: refine the tracked `docs/resume/resume-<facet>.json` (Flow 2a — write back).
- With `--jd`: produce a one-off export tailored to that specific JD (Flow 2b — **do NOT commit**, write to `/tmp/`).

## Step 1 — Load inputs

Read, in order:
1. `docs/resume/cv.json` — the ONLY source of facts. Invent nothing not derivable from it.
2. `docs/resume_split_blueprint.md` — the facet definition AND the truthfulness authority (the "不可宣稱" lists).
3. `docs/resume_tech_gap_filling.md` — what each facet still lacks (do not claim gaps as proficiencies).
4. The current `docs/resume/resume-<facet>.json` if it exists (you are refining it).
5. If `--jd` was given, read that JD (URL → fetch; path → read).

## Step 2 — Analyze and propose

Compare the facet resume against the facet spec (and the JD, if given). Produce truthful edits only:
- `basics.label` / `basics.summary` to the facet angle.
- `work[*].highlights` reframed to the facet's foreground (same facts, different emphasis).
- `skills` reordered per the blueprint's facet ordering.
- `projects` selected per the blueprint.
- Mark anything in-progress inline, e.g. `"Delta Lake (learning)"`, `"GraphRAG (in-progress)"`.

**Invariant fields** (basics contact, work employer/position/dates/location, education, languages) must be
**copied verbatim from `cv.json`** — never tailored (decision #13).

**Hard truthfulness rules** (from the blueprint — enforce strictly):
- MediaTek used Beam/Dataflow, **never Spark/PySpark**.
- IaC is Helm + ArgoCD, **never Terraform**.
- AWS = model-monitoring only, **not** platform depth.
- RAG/LangGraph/GraphRAG = **(in-progress)**, never "proficient/completed".

Present a numbered list of suggested changes (reason + proposed value), then **stop and wait** for the user's
natural-language reply (accept all / accept some / tweak). Mirror the `/cv-sync` approval UX.

## Step 3 — Apply

Build the complete updated JSON. Validate it parses.
- No `--jd`: write to `docs/resume/resume-<facet>.json`. Then run `make cv-lint` and report the result.
- With `--jd`: write to `/tmp/resume-<facet>-<jd-slug>.json` (ephemeral; not committed). Tell the user the path and that `make cv-render` can turn it into a PDF.

Print a short summary of what changed and any truthfulness guardrail you applied.
