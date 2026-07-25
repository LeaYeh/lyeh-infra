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


from resume_md import fingerprint, parse_bullet


def test_parse_bullet_plain():
    b = parse_bullet("- Cut CI feedback loop from 20 min to 4 min", 12)
    assert b.text == "Cut CI feedback loop from 20 min to 4 min"
    assert b.id is None
    assert b.src is None
    assert b.line == 12


def test_parse_bullet_with_id():
    b = parse_bullet("- Drove the GitOps migration {#csense-h1}", 5)
    assert b.text == "Drove the GitOps migration"
    assert b.id == "csense-h1"


def test_parse_bullet_with_src_anchor():
    b = parse_bullet("- Owned the GitOps delivery path <!-- src: csense-h1 @4f2a -->", 9)
    assert b.text == "Owned the GitOps delivery path"
    assert b.src == "csense-h1"
    assert b.src_hash == "4f2a"


def test_parse_bullet_rejects_non_bullet():
    with pytest.raises(MdError):
        parse_bullet("not a bullet", 3)


def test_fingerprint_is_whitespace_insensitive_and_four_hex():
    a = fingerprint("Drove   the GitOps\nmigration")
    b = fingerprint("Drove the GitOps migration")
    assert a == b
    assert len(a) == 4
    assert all(c in "0123456789abcdef" for c in a)
