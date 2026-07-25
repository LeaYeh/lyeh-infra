import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from resume_md import MdError, parse
from jsonresume_map import to_jsonresume

DOC = '''+++
name = "Lea"
email = "lea@example.com"

[location]
city = "Vienna"
countryCode = "AT"

[[profiles]]
network = "LinkedIn"
url = "https://example.com/in/lea"
+++

# Summary

Senior engineer.

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
end = ""
location = "Vienna, Austria"
-->

c-sense builds sensors.

- Drove the GitOps migration {#csense-h1}

# Skills

## Platform
<!--meta
level = "Advanced"
-->

- Kubernetes
- ArgoCD

# Languages

## German
<!--meta
fluency = "Beginner"
-->
'''


def test_basics_come_from_frontmatter_and_summary_section():
    data, _ = to_jsonresume(parse(DOC))
    assert data["basics"]["name"] == "Lea"
    assert data["basics"]["location"]["city"] == "Vienna"
    assert data["basics"]["profiles"][0]["network"] == "LinkedIn"
    assert data["basics"]["summary"] == "Senior engineer."


def test_work_entry_maps_heading_meta_prose_and_highlights():
    data, _ = to_jsonresume(parse(DOC))
    work = data["work"][0]
    assert work["name"] == "c-sense GmbH"
    assert work["position"] == "Senior Software Engineer"
    assert work["startDate"] == "2024-08-01"
    assert work["endDate"] == ""
    assert work["location"] == "Vienna, Austria"
    assert work["summary"] == "c-sense builds sensors."
    assert work["highlights"] == ["Drove the GitOps migration"]
    assert "id" not in work


def test_skills_bullets_become_keywords():
    data, _ = to_jsonresume(parse(DOC))
    assert data["skills"][0] == {
        "name": "Platform",
        "level": "Advanced",
        "keywords": ["Kubernetes", "ArgoCD"],
    }


def test_absent_sections_become_empty_lists():
    data, _ = to_jsonresume(parse(DOC))
    assert data["projects"] == []
    assert data["interests"] == []


def test_schema_and_meta_constants_are_emitted():
    data, _ = to_jsonresume(parse(DOC))
    assert data["$schema"] == (
        "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
    )
    assert data["meta"]["version"] == "v1.0.0"


def test_line_map_anchors_paths_to_source_lines():
    data, lines = to_jsonresume(parse(DOC))
    assert lines["work[0]"] == 20
    assert lines["work[0].highlights[0]"] == 30


def test_unknown_section_is_rejected():
    with pytest.raises(MdError) as e:
        to_jsonresume(parse('+++\nname = "Lea"\n+++\n\n# Hobbies\n\nStuff.\n'))
    assert "Hobbies" in e.value.message


def test_id_on_a_non_id_section_is_rejected():
    bad = '+++\nname = "Lea"\n+++\n\n# Skills\n\n## Platform\n\n- Kubernetes {#skill-1}\n'
    with pytest.raises(MdError) as e:
        to_jsonresume(parse(bad))
    assert "Skills" in e.value.message
