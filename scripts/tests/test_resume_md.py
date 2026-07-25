import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_md import MdError, split_frontmatter, parse_meta_block


def test_split_frontmatter_returns_data_body_and_offset():
    text = '+++\nname = "Lea"\n+++\n\n# Summary\n\nHello\n'
    fm, body, first_line = split_frontmatter(text)
    assert fm == {"name": "Lea"}
    assert body[0] == ""
    assert body[1] == "# Summary"
    assert first_line == 4


def test_split_frontmatter_requires_opening_fence():
    with pytest.raises(MdError) as e:
        split_frontmatter("# Summary\n")
    assert e.value.line == 1
    assert "+++" in e.value.message


def test_split_frontmatter_rejects_unterminated_fence():
    with pytest.raises(MdError) as e:
        split_frontmatter('+++\nname = "Lea"\n')
    assert "unterminated" in e.value.message


def test_split_frontmatter_reports_toml_errors():
    with pytest.raises(MdError) as e:
        split_frontmatter("+++\nname = \n+++\n")
    assert "TOML" in e.value.message


def test_parse_meta_block_reads_toml_between_markers():
    lines = ["<!--meta", 'id = "csense"', 'start = "2024-08-01"', "-->", "rest"]
    meta, next_index = parse_meta_block(lines, 0, line_offset=10)
    assert meta == {"id": "csense", "start": "2024-08-01"}
    assert next_index == 4


def test_parse_meta_block_rejects_unterminated():
    with pytest.raises(MdError):
        parse_meta_block(["<!--meta", 'id = "x"'], 0, line_offset=1)
