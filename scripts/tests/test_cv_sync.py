import json
import os
from pathlib import Path
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))
from cv_sync import load_content, load_env, fetch_gist, update_gist


def test_load_content_collects_markdown(tmp_path):
    content_dir = tmp_path / "apps/portal/src/content"
    (content_dir / "posts").mkdir(parents=True)
    (content_dir / "projects").mkdir(parents=True)
    (content_dir / "about.md").write_text("# About\nHello")
    (content_dir / "posts/my-post.md").write_text("# Post\nWorld")
    (content_dir / "posts/_index.md").write_text("ignored")
    (content_dir / "projects/proj.md").write_text("# Proj\nStuff")
    (content_dir / "projects/_index.md").write_text("ignored")

    result = load_content(content_dir)

    assert "--- about.md ---" in result
    assert "Hello" in result
    assert "--- posts/my-post.md ---" in result
    assert "World" in result
    assert "--- projects/proj.md ---" in result
    assert "Stuff" in result
    assert "_index.md" not in result


def test_load_env_sets_missing_vars(tmp_path, monkeypatch):
    env_file = tmp_path / "cv-sync.env"
    env_file.write_text("GIST_ID=abc123\nGITHUB_TOKEN=tok\n")
    monkeypatch.delenv("GIST_ID", raising=False)
    load_env(env_file)
    assert os.environ["GIST_ID"] == "abc123"


def test_load_env_does_not_override_existing(tmp_path, monkeypatch):
    env_file = tmp_path / "cv-sync.env"
    env_file.write_text("GIST_ID=from_file\n")
    monkeypatch.setenv("GIST_ID", "from_shell")
    load_env(env_file)
    assert os.environ["GIST_ID"] == "from_shell"


def test_load_env_strips_quoted_values(tmp_path, monkeypatch):
    env_file = tmp_path / "cv-sync.env"
    env_file.write_text('GIST_ID="abc123"\n')
    monkeypatch.delenv("GIST_ID", raising=False)
    load_env(env_file)
    assert os.environ["GIST_ID"] == "abc123"


def test_fetch_gist_returns_resume_and_filename():
    resume = {"basics": {"name": "Lea Yeh"}}
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "files": {
            "resume.json": {"content": json.dumps(resume)}
        }
    }
    mock_resp.raise_for_status = MagicMock()

    with patch("cv_sync.requests.get", return_value=mock_resp) as mock_get:
        result, filename = fetch_gist("gist123", "token456")

    mock_get.assert_called_once_with(
        "https://api.github.com/gists/gist123",
        headers={"Authorization": "token token456", "Accept": "application/vnd.github.v3+json"},
    )
    assert result == resume
    assert filename == "resume.json"


def test_fetch_gist_raises_when_no_json_file():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"files": {"notes.txt": {"content": "hi"}}}
    mock_resp.raise_for_status = MagicMock()

    with patch("cv_sync.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="No JSON file"):
            fetch_gist("gist123", "token456")


def test_update_gist_patches_correct_endpoint():
    resume = {"basics": {"name": "Lea Yeh"}}
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch("cv_sync.requests.patch", return_value=mock_resp) as mock_patch:
        update_gist("gist123", "token456", "resume.json", resume)

    mock_patch.assert_called_once_with(
        "https://api.github.com/gists/gist123",
        headers={"Authorization": "token token456", "Accept": "application/vnd.github.v3+json"},
        json={"files": {"resume.json": {"content": json.dumps(resume, indent=2, ensure_ascii=False)}}},
    )


from cv_sync import apply_patch


def test_apply_patch_replace_string_field():
    resume = {"basics": {"summary": "old summary"}}
    apply_patch(resume, "basics.summary", "replace", "new summary")
    assert resume["basics"]["summary"] == "new summary"


def test_apply_patch_append_to_array():
    resume = {"work": [{"highlights": ["existing"]}]}
    apply_patch(resume, "work[0].highlights", "append", "new highlight")
    assert resume["work"][0]["highlights"] == ["existing", "new highlight"]


def test_apply_patch_replace_array_element():
    resume = {"skills": [{"keywords": ["Python"]}]}
    apply_patch(resume, "skills[0].keywords", "replace", ["Python", "Go"])
    assert resume["skills"][0]["keywords"] == ["Python", "Go"]


def test_apply_patch_append_to_top_level_array():
    resume = {"work": [{"name": "Acme"}]}
    apply_patch(resume, "work", "append", {"name": "NewCo"})
    assert len(resume["work"]) == 2
    assert resume["work"][1]["name"] == "NewCo"
