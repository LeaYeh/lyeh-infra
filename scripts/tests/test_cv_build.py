import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from cv_build import build_file

GOOD = '''+++
name = "Lea"
email = "lea@example.com"
+++

# Summary

Senior engineer.

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
-->

- Drove the GitOps migration {#csense-h1}
'''

BAD_DATE = GOOD.replace('start = "2024-08-01"', 'start = "2024-08"')


def test_build_writes_json(tmp_path):
    md = tmp_path / "cv.md"
    md.write_text(GOOD)
    errors = build_file(md)
    assert errors == []
    data = json.loads((tmp_path / "cv.json").read_text())
    assert data["work"][0]["name"] == "c-sense GmbH"


def test_build_refuses_to_write_on_schema_error(tmp_path):
    md = tmp_path / "cv.md"
    md.write_text(BAD_DATE)
    (tmp_path / "cv.json").write_text('{"keep": "me"}')
    errors = build_file(md)
    assert errors
    assert json.loads((tmp_path / "cv.json").read_text()) == {"keep": "me"}


def test_schema_errors_carry_the_source_line(tmp_path):
    """work[0].startDate has no line of its own, so it falls back to the entry heading (line 12)."""
    md = tmp_path / "cv.md"
    md.write_text(BAD_DATE)
    errors = build_file(md)
    assert any(e.line == 12 and "YYYY-MM-DD" in e.message for e in errors)


def test_output_is_utf8_and_indented(tmp_path):
    md = tmp_path / "cv.md"
    md.write_text(GOOD.replace("Senior engineer.", "資深工程師。"))
    build_file(md)
    text = (tmp_path / "cv.json").read_text()
    assert "資深工程師。" in text
    assert '\n  "basics"' in text
