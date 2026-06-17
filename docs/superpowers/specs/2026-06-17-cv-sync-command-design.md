# /cv-sync Claude Code Command Design

**Date:** 2026-06-17
**Status:** Approved

## Goal

A project-local Claude Code slash command (`/cv-sync`) that reads lyeh-infra portal content and the JSON Resume gist, uses Claude's own intelligence to identify CV gaps, presents a numbered suggestion list in conversation, and applies user-selected changes directly to the gist.

## Relationship to Existing Tool

`scripts/cv_sync.py` (`make cv-sync`) remains the standalone CLI tool. This command is a native Claude Code alternative — Claude reads and reasons directly, no Python subprocess or external Anthropic API call needed.

## File

`.claude/commands/cv-sync.md` — project-local, available in any Claude Code session inside lyeh-infra.

## Prerequisites

- `scripts/cv-sync.env` with `GIST_ID=<id>`
- `GITHUB_TOKEN` in shell environment (gist read+write scope)

## Flow

```
/cv-sync
  1. Read scripts/cv-sync.env → extract GIST_ID
  2. Verify GITHUB_TOKEN in env (fail fast if missing)
  3. Read all portal content via Read tool:
       apps/portal/src/content/about.md
       apps/portal/src/content/posts/*.md   (skip _index.md)
       apps/portal/src/content/projects/*.md (skip _index.md)
  4. curl GET https://api.github.com/gists/$GIST_ID → extract JSON Resume
  5. Claude analyzes both → generates numbered suggestion list:
       [1] field: basics.summary | action: replace | reason + proposed value
       [2] field: work[0].highlights | action: append | reason + proposed value
       ...
  6. Wait for user natural-language response
       ("接受 1、3，把 2 改成更簡短的版本")
  7. Claude applies accepted/edited suggestions to in-memory JSON
  8. curl PATCH gist with updated JSON
  9. Confirm: "✓ Gist updated — N suggestions applied."
```

## Suggestion Format (in conversation)

```
找到 N 條建議：

**[1] basics.summary — replace**
理由：about.md 新增了 AI initiative，CV summary 未反映
建議：「Sr. Software Engineer ...（新版本）」

**[2] work[0].highlights — append**
理由：...

請告訴我要接受哪些，或如何調整。
```

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| `scripts/cv-sync.env` 不存在 | 印出設定步驟後停止 |
| `GIST_ID` 未設或空 | 提示填寫 cv-sync.env 後停止 |
| `GITHUB_TOKEN` 未設 | 提示設定 shell env 後停止 |
| gist 無 `.json` 檔 | 報錯：找不到 JSON Resume |
| curl HTTP error | 印出 HTTP status 後停止 |
| 無建議 | 回報「CV 目前是最新狀態」 |

## Applying Changes

Claude manipulates the JSON Resume in memory (no jq dependency). After user confirms selections, Claude writes the complete updated JSON and sends a single curl PATCH request. The gist always receives the full file content (not a diff).

## Out of Scope

- Canva/PDF resume (deferred)
- Auto-trigger on commit
- Posting to any other service
