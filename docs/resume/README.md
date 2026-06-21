# Resume SSOT & Tooling

Single source of truth for Lea Yeh's resume, plus the tools that derive
JD-tailored variants and render them to PDF.

Design rationale lives in [`raw/resume_ssot_spec.md`](raw/resume_ssot_spec.md).
This README is the practical "how to use it" guide.

> **Public repo note:** this is a public repository. Only the tooling and the
> de-sensitized resume JSON are committed. The `raw/` design docs, `jd-tracker.md`,
> and rendered `*.pdf` are **git-ignored (local-only)**, and the committed JSON has
> the phone number stripped (keep your real one in a local, uncommitted copy for
> rendering / publishing).

## CV vs. resume

| | CV (`cv.json`) | Resume (`resume-{a,b,c}.json`) |
|---|---|---|
| Purpose | Comprehensive intake pool — "包山包海" | JD-tailored pitch — grab attention in 30s |
| Content | Every role, project, award, cert, publication | Curated subset, reframed to one angle |
| Length when rendered | Multi-page (~4) | **One page** |
| Public? | Yes — published to a Gist | Tracked in repo, not auto-published |

**Facets:** A = Platform / Infrastructure / SRE · B = Data Engineer · C = MLOps / AI Platform.

## File layout

Committed (public):
```
docs/resume/
├── cv.json              # SSOT — the comprehensive CV (phone stripped)
├── resume-a.json        # facet A (Platform/Infra/SRE)
├── resume-b.json        # facet B (Data Engineer)
├── resume-c.json        # facet C (MLOps/AI Platform)
└── README.md            # this file
scripts/
├── cv_render.py         # JSON Resume -> HTML (two modes)
├── cv-lint.py           # drift backstop
└── cv-sync.env          # GIST_ID for publishing (git-ignored)
```

Local-only (git-ignored — see `.gitignore`):
```
docs/resume/
├── *.pdf                            # rendered output (regenerate via `make cv-render`)
├── jd-tracker.md                    # curated job descriptions (feeds /cv-tailor)
└── raw/
    ├── resume_ssot_spec.md          # design spec
    ├── resume_split_blueprint.md    # facet definitions + truthfulness rules ("不可宣稱")
    ├── resume_tech_gap_filling.md   # what each facet still lacks
    ├── Resume2026_origin.pdf        # original resume the renderer's look matches
    └── 2026 - JD_JR.txt             # raw JD inbox (paste new ones here)
```

## The three flows

```
        portal/blog ──/cv-sync──▶ cv.json ──/cv-tailor──▶ resume-{a,b,c}.json
                                     │                          │
                                     │ make cv-publish          │ make cv-render
                                     ▼                          ▼
                                  Gist (public)          PDFs (cv + 1-page resumes)
```

### 1. Intake — `/cv-sync` (assisted)

Folds new experiences from portal/blog content into `cv.json`. **Additive only**;
never touches invariant fields (contact, employer/dates, education, languages) and
never touches the Gist. Numbered-suggestion approval UX. Run the `/cv-sync` skill in
Claude Code. (`make cv-sync` just prints this reminder.)

### 2. Targeting — `/cv-tailor <a|b|c> [--jd <url>]` (assisted)

Curates `cv.json` into a facet resume, reframing the same facts to one angle and
enforcing the blueprint's truthfulness rules.

- **No `--jd`** → refines the tracked `resume-<facet>.json` (committed).
- **With `--jd`** → one-off export tailored to that JD, written to `/tmp/`
  (ephemeral, not committed).

Invariant fields are copied verbatim from `cv.json`. Run the `/cv-tailor` skill in
Claude Code. (`make cv-tailor` just prints this reminder.)

### 3. Publish — `make cv-publish` (deterministic)

Runs `cv-lint` first, then pushes `cv.json` to the public Gist
(`GIST_ID` in `scripts/cv-sync.env`) via `gh api`, and refreshes the
`apps/portal/src/data/resume.json` copy. Requires the `gh` CLI authenticated.

## Rendering to PDF — `make cv-render`

Renders every JSON in `docs/resume/` to PDF and writes the result alongside the JSON:

```bash
make cv-render
#   ✓ cv.pdf (cv)          ← detailed, multi-page
#   ✓ resume-a.pdf (resume)← one-page DM
#   ✓ resume-b.pdf (resume)
#   ✓ resume-c.pdf (resume)
```

`cv.json` renders in **`cv` mode** (detailed); `resume-*.json` render in **`resume`
mode** (one-page). Both share one visual language — a two-column layout (left
sidebar: skills / education / languages / certs; right: summary + experience),
teal accent, uppercase underlined section headers, bold lead bullet, round photo —
matching `raw/Resume2026_origin.pdf`.

Under the hood: `scripts/cv_render.py` turns JSON → self-contained HTML, then
headless Chrome prints it to PDF. The Chrome binary is auto-detected (macOS app,
`chromium`, `chromium-browser`, or `google-chrome`); override with
`make cv-render CHROME=/path/to/chrome`.

### Using the renderer directly

```bash
# one file to HTML (stdout or --out)
python3 scripts/cv_render.py docs/resume/resume-a.json --mode resume --out a.html
python3 scripts/cv_render.py docs/resume/cv.json        --mode cv     --out cv.html

# HTML -> PDF
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=a.pdf a.html
```

### Customizing the look

Open `scripts/cv_render.py`:

- **Layout knobs** (top of file): `RESUME_MAX_HIGHLIGHTS`, `RESUME_MAX_JOBS`,
  `RESUME_MAX_PROJECTS` cap content in resume mode to keep it on one page.
- **Colors:** `ACCENT`, `INK`, `MUTE`, `SIDEBAR_BG`.
- **Styling:** the `CSS` block — `.mode-resume` rules tighten spacing for the
  one-page variant; `.mode-cv` inherits the relaxed base.

> If a resume mode file ever overflows to a 2nd page, lower a `RESUME_MAX_*` cap or
> tighten the `.mode-resume` spacing — usually it's the longest sidebar (skills +
> certs) running taller than the experience column.

## Consistency check — `make cv-lint`

`cv.json` is the source of invariant truth. `scripts/cv-lint.py` verifies every
`resume-*.json` agrees with it on fields that must **not** be tailored:

- `basics`: name, email, phone, location
- each `work` entry: employer, position, startDate, endDate, location
- the whole `education` and `languages` arrays

Exits non-zero on drift (and prints the diff). Run it after any hand-edit;
`make cv-publish` runs it automatically.

```bash
make cv-lint
# ✓ invariants consistent across cv.json + 3 resume(s)
```

## Job-description workflow

`jd-tracker.md` is the curated catalog of interesting JDs, each tagged with the
best-fit facet and honest gap notes. Workflow:

1. Paste new raw JDs (URL or full text) into `raw/2026 - JD_JR.txt` (the inbox).
2. Ask Claude to fold them into `jd-tracker.md`.
3. To tailor a resume to a specific posting: `/cv-tailor <a|b|c> --jd <url>`.

## Requirements

- **python3** (stdlib only) — `cv_render.py`, `cv-lint.py`
- **Google Chrome / Chromium** — `make cv-render` (PDF printing)
- **gh CLI** (authenticated) — `make cv-publish` only

## Truthfulness rules (hard constraints)

Enforced by `/cv-tailor` and `/cv-sync`; see `raw/resume_split_blueprint.md` for the
full "不可宣稱" lists. Highlights:

- MediaTek used **Beam/Dataflow, never Spark/PySpark**.
- IaC is **Helm + ArgoCD, never Terraform**.
- AWS = **model-monitoring only**, not platform depth.
- RAG / LangGraph / agents = **(in-progress)**, never "proficient".
- German = **beginner**.
