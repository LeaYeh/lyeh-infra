import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from cv_lint import check_invariants, check_numbers, check_provenance, check_rules, load_rules
from resume_md import fingerprint

CV = '''+++
name = "Lea"
email = "lea@example.com"
phone = ""
+++

# Summary

Engineer.

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
end = ""
location = "Vienna, Austria"
-->

- Drove the GitOps migration {#csense-h1}

# Languages

## German
<!--meta
fluency = "Beginner"
-->
'''


def write(tmp_path, name, text):
    p = tmp_path / f"{name}.md"
    p.write_text(text)
    return p


def test_matching_invariants_pass(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", CV)
    assert check_invariants(cv, [facet]) == []


def test_drifting_employer_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", CV.replace("c-sense GmbH", "c-sense AG"))
    problems = check_invariants(cv, [facet])
    assert any("work" in p.message for p in problems)


def test_drifting_contact_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", CV.replace("lea@example.com", "other@example.com"))
    problems = check_invariants(cv, [facet])
    assert any("basics" in p.message for p in problems)


def test_drifting_languages_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", CV.replace('fluency = "Beginner"', 'fluency = "Fluent"'))
    problems = check_invariants(cv, [facet])
    assert any("languages" in p.message for p in problems)


SOURCE = "Drove the GitOps migration"
GOOD_ANCHOR = f"- Owned the GitOps delivery path <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"


def facet(bullet: str) -> str:
    return CV.replace("- Drove the GitOps migration {#csense-h1}", bullet)


def test_valid_anchor_passes(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet(GOOD_ANCHOR))
    assert check_provenance(cv, [f]) == []


def test_missing_anchor_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet("- Owned the GitOps delivery path"))
    problems = check_provenance(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "no src anchor" in problems[0].message


def test_dangling_id_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet("- Something <!-- src: ghost-h9 @0000 -->"))
    problems = check_provenance(cv, [f])
    assert problems[0].fatal
    assert "ghost-h9" in problems[0].message


def test_stale_fingerprint_warns_but_is_not_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet("- Owned it <!-- src: csense-h1 @dead -->"))
    problems = check_provenance(cv, [f])
    assert len(problems) == 1
    assert not problems[0].fatal
    assert "stale" in problems[0].message


def test_duplicate_ids_in_cv_are_fatal(tmp_path):
    dup = CV.replace(
        "- Drove the GitOps migration {#csense-h1}",
        "- Drove the GitOps migration {#csense-h1}\n- Cut the CI loop {#csense-h1}",
    )
    cv = write(tmp_path, "cv", dup)
    problems = check_provenance(cv, [])
    assert problems[0].fatal
    assert "duplicate" in problems[0].message


RULES = '''
[[banned]]
pattern = '\\bterraform\\b'
message = "IaC here is Helm + ArgoCD, never Terraform"

[[qualified]]
pattern = '\\b(graph)?rag\\b'
requires = '\\(in-progress\\)'
message = "RAG must be marked (in-progress)"
'''


def rules_file(tmp_path):
    p = tmp_path / "rules.toml"
    p.write_text(RULES)
    return load_rules(p)


def test_banned_term_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", facet("- Managed infra with Terraform"))
    problems = check_rules([f], rules_file(tmp_path))
    assert problems[0].fatal
    assert "Terraform" in problems[0].message


def test_qualified_term_without_qualifier_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", facet("- Built a RAG pipeline"))
    problems = check_rules([f], rules_file(tmp_path))
    assert problems and problems[0].fatal


def test_qualified_term_with_qualifier_passes(tmp_path):
    f = write(tmp_path, "resume-a", facet("- Built a RAG pipeline (in-progress)"))
    assert check_rules([f], rules_file(tmp_path)) == []


def test_number_absent_from_source_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet(f"- Migrated 12 services <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert problems[0].fatal
    assert "12" in problems[0].message


def test_number_present_in_source_passes(tmp_path):
    cv_text = CV.replace(SOURCE, "Drove the GitOps migration for 12 services")
    cv = write(tmp_path, "cv", cv_text)
    src_hash = fingerprint("Drove the GitOps migration for 12 services")
    f = write(tmp_path, "resume-a",
              facet(f"- Migrated 12 services <!-- src: csense-h1 @{src_hash} -->"))
    assert check_numbers(cv, [f]) == []


def test_digits_in_url_are_not_flagged(tmp_path):
    # docs/resume/resume-a.md:104 — a Google Slides link whose opaque doc ID
    # contains digit runs ('13', '3', '4') that are not metric claims.
    cv = write(tmp_path, "cv", CV)
    bullet = (
        "- Hosted a Git Essentials workshop — 'Something You Should Know Before "
        "Git Branch' — covering branching strategy, rebase, conflict resolution, "
        "and collaborative workflows (slides: "
        "https://docs.google.com/presentation/d/13InmNDRSfkeUnGWHNXWFiTr3QCAz4ecFL_wFz-NFdoI/edit?usp=sharing) "
        f"<!-- src: csense-h1 @{fingerprint(SOURCE)} -->"
    )
    f = write(tmp_path, "resume-a", facet(bullet))
    assert check_numbers(cv, [f]) == []


def test_digits_in_identifiers_are_not_flagged(tmp_path):
    # docs/resume/resume-a.md:164 — 'k3s' and 'CX23' are product names, not
    # quantities; the source bullet mentions neither.
    cv = write(tmp_path, "cv", CV)
    bullet = (
        "- Runs a k3s cluster on a Hetzner CX23 instance with ArgoCD "
        "continuously reconciling application state from Git "
        f"<!-- src: csense-h1 @{fingerprint(SOURCE)} -->"
    )
    f = write(tmp_path, "resume-a", facet(bullet))
    assert check_numbers(cv, [f]) == []


def test_percentage_claim_absent_from_source_is_still_fatal(tmp_path):
    # The highest-value case the gate protects: a standalone percentage claim
    # must still be caught even after narrowing what counts as a number.
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Cut cost 25% <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert problems and problems[0].fatal
    assert "25" in problems[0].message


def test_multiplier_claim_absent_from_source_is_still_fatal(tmp_path):
    # '5x' / '5×' is a standalone claim ("reduced build time 5x"), not an
    # identifier fragment — it must still be caught when unsupported.
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Reduced build time 5x <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert problems and problems[0].fatal
    assert "5" in problems[0].message


import json

from cv_build import build_file
from cv_lint import check_freshness


def test_matching_json_passes(tmp_path):
    md = write(tmp_path, "cv", CV)
    build_file(md)
    assert check_freshness([md]) == []


def test_stale_json_is_fatal(tmp_path):
    md = write(tmp_path, "cv", CV)
    (tmp_path / "cv.json").write_text(json.dumps({"basics": {"name": "Old"}}))
    problems = check_freshness([md])
    assert problems[0].fatal
    assert "cv-build" in problems[0].message


def test_missing_json_is_fatal(tmp_path):
    md = write(tmp_path, "cv", CV)
    assert check_freshness([md])[0].fatal
