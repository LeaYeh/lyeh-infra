Sync your JSON Resume (GitHub Gist) with lyeh-infra portal content.
Run from the lyeh-infra repo root.

**Language:** Traditional Chinese (zh-TW) for all user-facing output.

## Step 1 — Load config

Run:
```bash
cat scripts/cv-sync.env 2>/dev/null
```

Parse `GIST_ID` from the output (strip surrounding quotes and whitespace).
If the file is missing or GIST_ID is empty, print:

> `scripts/cv-sync.env` 不存在或 GIST_ID 未設定。
> 請建立檔案並填入：`GIST_ID=your-gist-id-here`

Then stop.

## Step 2 — Verify gh auth

Run:
```bash
gh auth status 2>&1
```

If the exit code is non-zero, print:

> `gh` 未登入，請執行 `gh auth login` 後再試。

Then stop.

## Step 3 — Read portal content

List available files:
```bash
ls apps/portal/src/content/posts/*.md \
   apps/portal/src/content/projects/*.md \
   apps/portal/src/content/about.md 2>/dev/null
```

Use the Read tool to read each file returned, **skipping any named `_index.md`**.
Hold all content in context for analysis.

## Step 4 — Fetch JSON Resume from Gist

Run (replace `$GIST_ID` with the value from Step 1):
```bash
gh api /gists/$GIST_ID
```

From the JSON response, locate the key inside `.files` whose name ends in `.json`.
Extract its `.content` field — that is the full JSON Resume text.
Parse it as JSON and hold in context.

If no `.json` file exists in the Gist, print an error and stop.

## Step 5 — Analyze and generate suggestions

Compare portal content with the JSON Resume. Check:
- `basics.summary` — does it reflect current role, focus, and recent work?
- `work[*].highlights` — are key achievements or projects from the portal missing?
- `skills[*].keywords` — are new technologies or skills mentioned in portal absent from CV?
- `projects[*]` — does the CV projects section align with portal project pages?

Present a numbered list in conversation:

```
找到 N 條建議：

**[1] basics.summary — replace**
理由：about.md 描述了 AI initiative，但 CV summary 未反映。
建議值：「...（完整建議內容）...」

**[2] work[0].highlights — append**
理由：...
建議值：「...」

請告訴我要接受哪些（例如「接受 1、3，把 2 改成更簡短的版本」），或說「全部接受」。
```

If no suggestions, print `CV 目前已是最新狀態，不需要更新。` and stop.

## Step 6 — Wait for user response

**Stop here.** Do not modify anything. Wait for the user's natural-language reply.

## Step 7 — Apply changes and update Gist

Based on the user's response, build the complete updated JSON Resume.

Write it to `/tmp/cv-sync-update.json` using the Write tool.

Then run (replace `$GIST_ID` and `$GIST_FILE` with actual values from Step 1 and Step 4):
```bash
GIST_FILE=resume.json
python3 -c "
import json, sys
with open('/tmp/cv-sync-update.json') as f:
    content = f.read()
payload = json.dumps({'files': {'$GIST_FILE': {'content': content}}})
sys.stdout.write(payload)
" | gh api -X PATCH /gists/$GIST_ID --input -

rm -f /tmp/cv-sync-update.json
```

If successful, print: `✓ Gist 已更新，套用了 N 條建議。`
If user skipped all suggestions: `未做任何變更。`
