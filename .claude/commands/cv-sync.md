Fold new experiences from portal/blog content into the comprehensive CV (`docs/resume/cv.md`).
Run from the lyeh-infra repo root.

**Language:** Traditional Chinese (zh-TW) for all user-facing output.

This is **Flow 1 (intake)** of the resume SSOT system: `portal content → cv.md`.
`docs/resume/cv.md` is the single source of truth and the comprehensive intake pool
("包山包海"); the facet resumes (`resume-{a,b,c}.md`) are derived from it separately via
`/cv-tailor`. `docs/resume/*.json` are **build artifacts** — `make cv-build` writes them,
you never hand-edit them. Publishing is a separate step (`make cv-publish`); this command
does NOT touch the Gist.

## Step 0 — Read the `cv-md` skill first (mandatory)

`cv.md` is **not free-form Markdown**. It has a `+++` TOML frontmatter, a fixed section
vocabulary, `<!--meta … -->` blocks, and two bullet annotations — and a build gate that
rejects anything else. Before writing a single line, read:

- `.claude/skills/cv-md/SKILL.md`
- `.claude/skills/cv-md/references/md-format.md` — the grammar: frontmatter keys,
  `# Section` / `## Entry` headings, meta blocks, prose, bullets, `{#id}`
- `.claude/skills/cv-md/references/anti-drafting.md` — the five gates and the only honest
  ways past them

Use that vocabulary in your proposals.

## Step 1 — Read portal content

List then read (skip any `_index.md`):
```bash
ls apps/portal/src/content/about.md \
   apps/portal/src/content/posts/*.md \
   apps/portal/src/content/projects/*.md 2>/dev/null
```
Hold all content in context.

## Step 2 — Read the current CV

Read `docs/resume/cv.md` in full. This is what you are extending. Note each entry's
`id` from its `<!--meta` block and the highest `-h<n>` already used in that entry — you
will need both in Step 5.

## Step 3 — Analyze: what is in portal content but not yet in the CV?

Compare. Look for experiences worth folding in:
- New **projects** described in `projects/*.md` or posts that have no `## ` entry under
  `# Projects` in `cv.md`.
- New **skills / technologies** mentioned in `about.md` ("Current" / "Exploring") missing
  from the bullets under `# Skills` (these become `keywords`).
- New **achievements or work facets** (e.g. the c-sense AI-initiative track in `about.md`)
  not yet in the relevant `# Work` entry's bullet list (these become `highlights`).

## Step 4 — Propose (numbered, then STOP)

Present a numbered list, each with reason + the exact Markdown line(s) you would add:

```
找到 N 條可折入 cv.md 的內容：

**[1] # Projects — 新增 "JD Analyzer"**
理由：projects/ 有此專案頁，cv.md 的 # Projects 尚無對應 ## 條目。
建議值：
    ## jd-explorer — JD Scraper & AI Analyzer
    <!--meta
    id = "jd-explorer"
    url = "https://github.com/LeaYeh/jd-explorer"
    -->

    FastAPI + Playwright ...

    - ... {#jd-explorer-h1}

**[2] # Work / c-sense (id = "csense") — 追加 highlight**
理由：about.md 描述 AI initiative，cv.md 未反映。
建議值：`- ... (in-progress) {#csense-h7}`   ← csense 目前最大編號為 h6
```

Then **stop and wait** for the user's natural-language reply (e.g. 「接受 1、3」/「全部接受」).

## Step 5 — Apply (additive only)

Based on the reply, edit `docs/resume/cv.md`:

- **ADDITIVE ONLY** — never delete or reword existing content.
- **Never touch invariant fields**: the frontmatter contact block (`name`, `email`,
  `phone`, `location`), any `## <employer> — <position>` heading, any `start` / `end` /
  `location` in a Work meta block, and the whole `# Education` and `# Languages` sections.
  The invariants gate compares these field-by-field against every `resume-*.md`.
- **Every new bullet under `# Work`, `# Volunteer` or `# Projects` gets a fresh, unique
  `{#<entry-id>-h<n>}` ID.** `<entry-id>` is the `id` from that entry's meta block;
  `<n>` is the next free number in that entry. IDs must be unique across `cv.md` — a
  repeat is reported as `duplicate bullet ID '<id>'` and the second bullet drops out of
  the provenance index, so facet anchors silently resolve to the wrong bullet.
  **Never renumber existing bullets** — every facet anchor pointing at them would break.
  Append with the next free number even when inserting in the middle.
- **Bullets that become `keywords` (`# Skills`) or `courses` (`# Education`) must NOT
  carry an ID.** That is a hard build error:
  `'Skills' bullets must not carry a {#id}`.
- Ground every addition in the portal source; **invent nothing**. If the portal text does
  not support a claim, do not write it — say what is missing and stop.
- Mark in-progress work `(in-progress)` **inside the same bullet**. `docs/resume/rules.toml`
  requires the qualifier in the bullet itself; a qualifier in the prose or a neighbouring
  bullet does not satisfy the gate.
- Match the existing Markdown style: em dash `—` in headings, TOML in meta blocks,
  hard-wrapping is free (prose lines are joined, bullet fingerprints normalise whitespace).

## Step 6 — Build and check

```bash
make cv-build && make cv-lint
```

Report **both** outputs to the user.

- `make cv-build` is schema-gated and writes **nothing** for a file that fails, so a
  failure means the old JSON is still on disk — fix the reported line in the `.md` and
  build again, never edit the JSON.
- `make cv-lint` runs the five gates. There are pre-existing findings in this corpus that
  are content decisions for the repo owner; do not "fix" them by inventing anchors or
  rewording claims you cannot verify. Report them and stop.

Then remind the user that `/cv-tailor <facet>` re-derives the facet resumes (new CV
bullets are not automatically pulled into them) and `make cv-publish` publishes the CV.
If no new content was found, print `cv.md 已涵蓋 portal 內容，無需更新。` and stop.
