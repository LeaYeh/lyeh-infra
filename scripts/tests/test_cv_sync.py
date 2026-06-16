import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from cv_sync import load_content, load_env


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
