import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_md import META_OPEN, MdError, split_frontmatter, parse_meta_block


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


def test_fingerprint_distinguishes_different_text():
    # The staleness check rests on this: different text must fingerprint
    # differently, otherwise an edited bullet still matches its old anchor.
    assert fingerprint("Drove the GitOps migration") != fingerprint("Cut the CI loop")
    assert fingerprint("Drove the GitOps migration") != fingerprint("Drove the GitOps migrations")


from resume_md import parse

DOC = '''+++
name = "Lea"
+++

# Summary

Senior engineer
and architect.

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
-->

c-sense builds sensors.

- Drove the GitOps migration {#csense-h1}
- Cut the CI loop {#csense-h2}

## MediaTek — Data Engineer
<!--meta
id = "mtk"
start = "2018-01-01"
-->

- Built pipelines {#mtk-h1}
'''


def test_parse_returns_frontmatter():
    doc = parse(DOC)
    assert doc.frontmatter == {"name": "Lea"}


def test_parse_collects_sections_in_order():
    doc = parse(DOC)
    assert [s.title for s in doc.sections] == ["Summary", "Work"]


def test_parse_section_prose_joins_wrapped_lines():
    doc = parse(DOC)
    assert doc.sections[0].prose == "Senior engineer and architect."


def test_parse_entry_heading_meta_prose_and_bullets():
    work = parse(DOC).sections[1]
    assert [e.heading for e in work.entries] == [
        "c-sense GmbH — Senior Software Engineer",
        "MediaTek — Data Engineer",
    ]
    first = work.entries[0]
    assert first.meta["id"] == "csense"
    assert first.prose == "c-sense builds sensors."
    assert [b.id for b in first.bullets] == ["csense-h1", "csense-h2"]


def test_parse_records_line_numbers():
    work = parse(DOC).sections[1]
    assert work.entries[0].line == 12
    assert work.entries[0].bullets[0].line == 20


def test_parse_rejects_entry_before_any_section():
    with pytest.raises(MdError):
        parse('+++\nname = "Lea"\n+++\n\n## Orphan entry\n')


def test_document_section_looks_up_by_title_and_misses_return_none():
    doc = parse(DOC)
    assert doc.section("Work") is doc.sections[1]
    assert doc.section("Summary") is doc.sections[0]
    assert doc.section("Education") is None


FACET_DOC = '''+++
name = "Lea"
variant = "a"
+++

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
-->

Derived one-pager prose.

- Owned the GitOps delivery path <!-- src: csense-h1 @4f2a -->
- Cut the CI loop <!-- src: csense-h2 @9b0c -->
'''


def test_parse_facet_document_with_provenance_anchors():
    doc = parse(FACET_DOC)
    entry = doc.section("Work").entries[0]
    assert entry.meta["id"] == "csense"
    assert entry.prose == "Derived one-pager prose."
    assert [b.text for b in entry.bullets] == [
        "Owned the GitOps delivery path",
        "Cut the CI loop",
    ]
    assert [b.src for b in entry.bullets] == ["csense-h1", "csense-h2"]
    assert [b.src_hash for b in entry.bullets] == ["4f2a", "9b0c"]
    assert [b.id for b in entry.bullets] == [None, None]
    assert [b.line for b in entry.bullets] == [16, 17]


# --- bullet annotations -------------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "- Owned it {#csense-h1} <!-- src: csense-h1 @4f2a -->",
        "- Owned it <!-- src: csense-h1 @4f2a --> {#csense-h1}",
    ],
)
def test_parse_bullet_round_trips_id_and_src_in_either_order(line):
    b = parse_bullet(line, 7)
    assert b.text == "Owned it"
    assert b.id == "csense-h1"
    assert b.src == "csense-h1"
    assert b.src_hash == "4f2a"


@pytest.mark.parametrize(
    "line",
    [
        "- Owned it <!-- src: csense-h1 @4F2A -->",  # uppercase hex
        "- Owned it <!-- src: csense-h1 @4f2 -->",  # three hex chars
        "- Owned it <!-- src: csense-h1 @4f2ab -->",  # five hex chars
        "- Owned it <!-- src: csense-h1 -->",  # no hash
        "- Owned it <!-- src csense-h1 @4f2a -->",  # missing colon
        "- Owned it {# csense-h1}",  # space inside the braces
        "- Owned it {#csense h1}",  # space inside the id
    ],
)
def test_parse_bullet_rejects_malformed_annotations(line):
    with pytest.raises(MdError) as e:
        parse_bullet(line, 42)
    assert e.value.line == 42
    assert "{#some-id}" in e.value.message
    assert "<!-- src: some-id @abcd -->" in e.value.message


@pytest.mark.parametrize(
    "line",
    [
        # Embedded src anchor: the bullet's real (trailing) src anchor is
        # stripped first, but a second, mid-text one must still be rejected.
        "- Designed the layered framework <!-- src: csense-h9 @beef --> end to "
        "end <!-- src: csense-h3 @d85d -->",
        # Embedded id: same shape, with a {#id} in the middle instead.
        "- Designed the layered {#csense-h9} framework end to end {#csense-h3}",
    ],
)
def test_parse_bullet_rejects_embedded_annotation(line):
    with pytest.raises(MdError) as e:
        parse_bullet(line, 42)
    assert e.value.line == 42
    assert "{#some-id}" in e.value.message
    assert "<!-- src: some-id @abcd -->" in e.value.message


def test_parse_bullet_accepts_tab_separated_marker():
    b = parse_bullet("-\tTabbed bullet", 3)
    assert b.text == "Tabbed bullet"


def test_parse_routes_tab_separated_bullets_as_bullets():
    doc = parse('+++\nname = "Lea"\n+++\n\n# Work\n\n## Acme\n\n-\tTabbed bullet\n')
    entry = doc.section("Work").entries[0]
    assert [b.text for b in entry.bullets] == ["Tabbed bullet"]
    assert entry.prose == ""


# --- error line numbers -------------------------------------------------


def test_meta_block_before_any_entry_reports_its_own_line():
    text = '+++\nname = "Lea"\n+++\n\n# Work\n\n<!--meta\nid = "x"\n-->\n'
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 7


def test_bullet_before_any_entry_reports_its_own_line():
    text = '+++\nname = "Lea"\n+++\n\n# Work\n\n- Orphan bullet\n'
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 7
    assert "Work" in e.value.message


def test_bullet_before_any_section_reports_its_own_line():
    text = '+++\nname = "Lea"\n+++\n\n- Orphan bullet\n'
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 5


def test_prose_before_any_section_reports_its_own_line():
    text = '+++\nname = "Lea"\n+++\n\n\n\nLoose prose here\n'
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 7


def test_entry_multiple_prose_paragraphs_join_with_blank_line():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n\n"  # 7-8
        "First paragraph.\n\n"  # 9-10
        "Second paragraph.\n\n"  # 11-12
        "- Did a thing\n"  # 13
    )
    doc = parse(text)
    entry = doc.section("Work").entries[0]
    assert entry.prose == "First paragraph.\n\nSecond paragraph."
    assert [b.text for b in entry.bullets] == ["Did a thing"]


def test_section_multiple_prose_paragraphs_join_with_blank_line():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Summary\n\n"  # 5-6
        "First paragraph\nwrapped.\n\n"  # 7-9
        "Second paragraph.\n"  # 10
    )
    doc = parse(text)
    prose = doc.sections[0].prose
    assert prose == "First paragraph wrapped.\n\nSecond paragraph."
    assert prose.split("\n\n") == ["First paragraph wrapped.", "Second paragraph."]


def test_three_prose_paragraphs_join_in_order():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Summary\n\n"  # 5-6
        "First.\n\n"  # 7-8
        "Second.\n\n"  # 9-10
        "Third.\n"  # 11
    )
    doc = parse(text)
    assert doc.sections[0].prose == "First.\n\nSecond.\n\nThird."


def test_prose_after_bullets_is_an_error():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n\n"  # 7-8
        "- Did a thing\n\n"  # 9-10
        "Stray prose after the bullets.\n"  # 11
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 11
    assert "before the bullet" in e.value.message
    assert "Acme" in e.value.message


def test_two_paragraph_summary_round_trips_through_split():
    paragraphs = [
        "Senior engineer with a decade of infra experience.",
        "Believes in boring technology.",
    ]
    original = "\n\n".join(paragraphs)
    md = (
        '+++\nname = "Lea"\n+++\n\n'
        "# Summary\n\n"
        + "\n\n".join(paragraphs)
        + "\n"
    )
    doc = parse(md)
    assert doc.sections[0].prose == original


def test_second_meta_block_reports_the_second_block_line():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n"  # 7
        '<!--meta\nid = "a"\n-->\n'  # 8-10
        '<!--meta\nstart = "2024-01-01"\n-->\n'  # 11-13
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 11
    assert "Acme" in e.value.message


def test_content_on_the_meta_open_line_is_an_error():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n"  # 7
        '<!--meta id = "x"\n-->\n'  # 8-9
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 8
    assert META_OPEN in e.value.message


def test_metadata_lookalike_comment_is_an_error_not_a_meta_block():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n"  # 7
        "<!--metadata blah\n-->\n"  # 8-9
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 8


def test_malformed_anchor_in_document_reports_the_bullet_line():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n\n"  # 7-8
        "- Owned it <!-- src: csense-h1 @4F2A -->\n"  # 9
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 9


def test_unterminated_meta_block_reports_the_opening_line():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n"  # 7
        '<!--meta\nid = "x"\n'  # 8-9
    )
    with pytest.raises(MdError) as e:
        parse(text)
    assert e.value.line == 8


# --- TOML error positions -----------------------------------------------


def test_frontmatter_toml_error_reports_the_offending_source_line():
    with pytest.raises(MdError) as e:
        split_frontmatter('+++\nname = "Lea"\nbad = \n+++\n')
    assert e.value.line == 3


def test_meta_block_toml_error_reports_the_offending_source_line():
    lines = ["<!--meta", 'id = "x"', "bad = ", "-->"]
    with pytest.raises(MdError) as e:
        parse_meta_block(lines, 0, line_offset=10)
    assert e.value.line == 12


# --- line splitting -----------------------------------------------------


def test_crlf_input_yields_correct_line_numbers():
    doc = parse(DOC.replace("\n", "\r\n"))
    work = doc.section("Work")
    assert work.entries[0].line == 12
    assert work.entries[0].bullets[0].line == 20
    assert doc.sections[0].prose == "Senior engineer and architect."


def test_exotic_line_separators_do_not_shift_line_numbers():
    text = (
        '+++\nname = "Lea"\n+++\n\n'  # 1-4
        "# Work\n\n"  # 5-6
        "## Acme\n\n"  # 7-8
        "Prose with a\x0cform feed, a separator and a\x85next line.\n\n"  # 9-10
        "- Bullet {#acme-h1}\n"  # 11
    )
    entry = parse(text).section("Work").entries[0]
    assert entry.bullets[0].line == 11
    assert entry.prose == "Prose with a form feed, a separator and a next line."
