Fold new experiences from portal/blog content into the comprehensive CV (`docs/resume/cv.json`).
Run from the lyeh-infra repo root.

**Language:** Traditional Chinese (zh-TW) for all user-facing output.

This is **Flow 1 (intake)** of the resume SSOT system (see `docs/resume_ssot_spec.md`):
`portal content → cv.json`. cv.json is the comprehensive intake pool ("包山包海"); tailored
resumes are derived from it separately via `/cv-tailor`. Publishing cv.json → Gist is a
separate step (`make cv-publish`). This command does NOT touch the Gist.

## Step 1 — Read portal content

List then read (skip any `_index.md`):
```bash
ls apps/portal/src/content/about.md \
   apps/portal/src/content/posts/*.md \
   apps/portal/src/content/projects/*.md 2>/dev/null
```
Hold all content in context.

## Step 2 — Read the current CV

Read `docs/resume/cv.json` (JSON Resume schema). This is what you are extending.

## Step 3 — Analyze: what is in portal content but not yet in the CV?

Compare. Look for experiences worth folding in:
- New **projects** described in `projects/*.md` or posts that are absent from `cv.json.projects`.
- New **skills / technologies** mentioned in `about.md` ("Current" / "Exploring") missing from `cv.json.skills`.
- New **achievements or work facets** (e.g. the c-sense AI-initiative track in `about.md`) not yet in the relevant `work[*].highlights`.

## Step 4 — Propose (numbered, then STOP)

Present a numbered list, each with reason + proposed value:

```
找到 N 條可折入 cv.json 的內容：

**[1] projects — add "JD Analyzer"**
理由：projects/ 有此專案頁，cv.json.projects 尚無。
建議值：{ "name": "...", "description": "...", "url": "..." }

**[2] work[0] (c-sense) highlights — append**
理由：about.md 描述 AI initiative，cv.json 未反映。
建議值：「...」
```

Then **stop and wait** for the user's natural-language reply (e.g. 「接受 1、3」/「全部接受」).

## Step 5 — Apply (additive only)

Based on the reply, build the updated `cv.json`:
- **ADDITIVE ONLY** — never delete or reword existing content.
- **Never touch invariant fields**: basics contact, work employer/position/dates/location, education, languages.
- Ground every addition in the portal source; **invent nothing**. Mark in-progress work `(in-progress)`.
- Keep JSON Resume schema valid; match existing style (indent 2, non-ASCII preserved).

Write `docs/resume/cv.json`, then run `make cv-lint` and report its result.
Remind the user that `/cv-tailor <facet>` re-derives the resumes and `make cv-publish` publishes the CV.
If no new content was found, print `cv.json 已涵蓋 portal 內容，無需更新。` and stop.
