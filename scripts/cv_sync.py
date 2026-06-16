# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic", "requests"]
# ///

import json
import os
import re
from pathlib import Path

import anthropic
import requests


def load_env(env_file: Path | None = None) -> None:
    if env_file is None:
        env_file = Path(__file__).parent / "cv-sync.env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), val)


def load_content(content_dir: Path | None = None) -> str:
    if content_dir is None:
        content_dir = Path(__file__).parent.parent / "apps/portal/src/content"
    files = [
        content_dir / "about.md",
        *sorted((content_dir / "posts").glob("*.md")),
        *sorted((content_dir / "projects").glob("*.md")),
    ]
    parts = []
    for f in files:
        if f.name == "_index.md" or not f.exists():
            continue
        parts.append(f"--- {f.relative_to(content_dir)} ---\n{f.read_text()}")
    return "\n\n".join(parts)


def fetch_gist(gist_id: str, token: str) -> tuple[dict, str]:
    resp = requests.get(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
    )
    resp.raise_for_status()
    for filename, file_data in resp.json()["files"].items():
        if filename.endswith(".json"):
            return json.loads(file_data["content"]), filename
    raise ValueError(f"No JSON file found in gist {gist_id}")


def update_gist(gist_id: str, token: str, filename: str, resume: dict) -> None:
    resp = requests.patch(
        f"https://api.github.com/gists/{gist_id}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
        json={"files": {filename: {"content": json.dumps(resume, indent=2, ensure_ascii=False)}}},
    )
    resp.raise_for_status()


def _parse_path(path: str) -> list[str | int]:
    """Parse 'work[0].highlights' → ['work', 0, 'highlights']."""
    tokens: list[str | int] = []
    for part in path.split("."):
        m = re.match(r"^(\w+)\[(\d+)\]$", part)
        if m:
            tokens.append(m.group(1))
            tokens.append(int(m.group(2)))
        else:
            tokens.append(part)
    return tokens


def apply_patch(resume: dict, field: str, action: str, value) -> None:
    tokens = _parse_path(field)
    obj = resume
    for token in tokens[:-1]:
        obj = obj[token]
    last = tokens[-1]
    if action == "append":
        obj[last].append(value)
    else:
        obj[last] = value


SUGGEST_TOOL = {
    "name": "suggest_cv_updates",
    "description": "Return CV update suggestions based on comparing portal content with the JSON Resume",
    "input_schema": {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {
                            "type": "string",
                            "description": "dot-path to the JSON Resume field, e.g. 'work[0].highlights' or 'basics.summary'",
                        },
                        "reason": {"type": "string"},
                        "action": {"type": "string", "enum": ["append", "replace"]},
                        "value": {"description": "string to append, or replacement value"},
                    },
                    "required": ["field", "reason", "action", "value"],
                },
            }
        },
        "required": ["suggestions"],
    },
}

_SYSTEM = (
    "You are a CV assistant. Given portal content (markdown) and a JSON Resume, "
    "identify information present in the portal but missing or outdated in the CV. "
    "Focus on: work experience highlights, skills, project descriptions, professional summary. "
    "Return suggestions using the suggest_cv_updates tool. "
    "Only suggest changes that would genuinely improve the CV. "
    "Reference existing JSON Resume fields by dot-path."
)


def interactive_loop(suggestions: list[dict], resume: dict) -> list[dict]:
    accepted = []
    total = len(suggestions)
    for i, s in enumerate(suggestions, 1):
        print(f"\n[{i}/{total}] {s['field']} — {s['action']}")
        print(f"  Reason : {s['reason']}")
        print(f"  Value  : {json.dumps(s['value'], ensure_ascii=False)}")
        while True:
            choice = input("  → [y] accept / [n] skip / [e] edit: ").strip().lower()
            if choice == "y":
                try:
                    apply_patch(resume, s["field"], s["action"], s["value"])
                    accepted.append(s)
                except (KeyError, IndexError, AttributeError) as exc:
                    print(f"  ✗ Could not apply patch ({exc}). Skipping.")
                break
            elif choice == "n":
                break
            elif choice == "e":
                raw = input("  New value: ").strip()
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError:
                    value = raw
                try:
                    apply_patch(resume, s["field"], s["action"], value)
                    accepted.append({**s, "value": value})
                except (KeyError, IndexError, AttributeError) as exc:
                    print(f"  ✗ Could not apply patch ({exc}). Skipping.")
                break
    return accepted


def get_suggestions(content: str, resume: dict, api_key: str) -> list[dict]:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        tools=[SUGGEST_TOOL],
        tool_choice={"type": "tool", "name": "suggest_cv_updates"},
        messages=[{
            "role": "user",
            "content": (
                f"Portal content:\n\n{content}\n\n"
                f"Current JSON Resume:\n\n{json.dumps(resume, indent=2)}"
            ),
        }],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "suggest_cv_updates":
            return block.input["suggestions"]
    return []


def main() -> None:
    load_env()

    gist_id = os.environ.get("GIST_ID")
    github_token = os.environ.get("GITHUB_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    missing = [k for k, v in {"GIST_ID": gist_id, "GITHUB_TOKEN": github_token, "ANTHROPIC_API_KEY": api_key}.items() if not v]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        print("Set them in your shell or in scripts/cv-sync.env (for GIST_ID)")
        raise SystemExit(1)

    print("Reading portal content...")
    content = load_content()

    print("Fetching JSON Resume from gist...")
    resume, filename = fetch_gist(gist_id, github_token)

    print("Asking Claude for suggestions...")
    suggestions = get_suggestions(content, resume, api_key)

    if not suggestions:
        print("No suggestions — CV looks up to date.")
        return

    print(f"\nFound {len(suggestions)} suggestion(s).\n")
    accepted = interactive_loop(suggestions, resume)

    if accepted:
        print(f"\nUpdating gist ({len(accepted)}/{len(suggestions)} accepted)...")
        update_gist(gist_id, github_token, filename, resume)
        print("✓ Gist updated.")
    else:
        print("\nNo changes applied.")


if __name__ == "__main__":
    main()
