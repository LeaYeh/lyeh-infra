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


def test_magnitude_suffix_claim_absent_from_source_is_fatal(tmp_path):
    # '14K' is a real metric (see docs/resume/cv.md) — a magnitude suffix
    # must not hide the digits from the gate the way an identifier does.
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Reached 14K users <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert problems and problems[0].fatal
    assert "14K" in problems[0].message


def test_magnitude_suffix_claim_present_in_source_passes(tmp_path):
    cv_text = CV.replace(SOURCE, "Drove the GitOps migration reaching 14K users")
    cv = write(tmp_path, "cv", cv_text)
    src_hash = fingerprint("Drove the GitOps migration reaching 14K users")
    f = write(tmp_path, "resume-a",
              facet(f"- Reached 14K users <!-- src: csense-h1 @{src_hash} -->"))
    assert check_numbers(cv, [f]) == []


def test_digits_before_non_magnitude_letter_are_not_flagged(tmp_path):
    # '3D' is not a metric claim — 'D' is not a magnitude suffix, unlike K/M/B.
    cv = write(tmp_path, "cv", CV)
    bullet = (
        "- Rendered a 3D scene visualization "
        f"<!-- src: csense-h1 @{fingerprint(SOURCE)} -->"
    )
    f = write(tmp_path, "resume-a", facet(bullet))
    assert check_numbers(cv, [f]) == []


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


# --- malformed documents are Problems, not exceptions -------------------

BROKEN = '''+++
name = "Lea"
+++

- Orphan bullet before any section
'''


def test_malformed_facet_is_reported_as_a_problem_in_invariants(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", BROKEN)
    problems = check_invariants(cv, [facet])
    assert len(problems) == 1
    assert problems[0].file == "resume-a.md"
    assert problems[0].line == 5
    assert problems[0].fatal


def test_malformed_cv_is_reported_as_a_problem_in_invariants(tmp_path):
    cv = write(tmp_path, "cv", BROKEN)
    facet = write(tmp_path, "resume-a", CV)
    problems = check_invariants(cv, [facet])
    assert len(problems) == 1
    assert problems[0].file == "cv.md"
    assert problems[0].fatal


def test_malformed_document_is_reported_as_a_problem_in_provenance(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", BROKEN)
    problems = check_provenance(cv, [facet])
    assert len(problems) == 1
    assert problems[0].file == "resume-a.md"
    assert problems[0].fatal


def test_provenance_still_checks_other_facets_after_one_is_malformed(tmp_path):
    cv = write(tmp_path, "cv", CV)
    broken_facet = write(tmp_path, "resume-a", BROKEN)
    good_facet = write(tmp_path, "resume-b", facet(GOOD_ANCHOR))
    problems = check_provenance(cv, [broken_facet, good_facet])
    # Only the malformed document is reported; resume-b.md was still
    # checked (its valid anchor produced no problem of its own).
    assert len(problems) == 1
    assert problems[0].file == "resume-a.md"


def test_malformed_document_is_reported_as_a_problem_in_rules(tmp_path):
    facet = write(tmp_path, "resume-a", BROKEN)
    problems = check_rules([facet], load_rules())
    assert len(problems) == 1
    assert problems[0].file == "resume-a.md"
    assert problems[0].fatal


def test_malformed_document_is_reported_as_a_problem_in_numbers(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", BROKEN)
    problems = check_numbers(cv, [facet])
    assert len(problems) == 1
    assert problems[0].file == "resume-a.md"
    assert problems[0].fatal


def test_malformed_document_is_reported_as_a_problem_in_freshness(tmp_path):
    md = write(tmp_path, "cv", BROKEN)
    (tmp_path / "cv.json").write_text("{}")  # must exist to reach the parse step
    problems = check_freshness([md])
    assert len(problems) == 1
    assert problems[0].file == "cv.md"
    assert problems[0].fatal


# --- the gates must see prose, labels and unit-bearing numbers ----------
#
# Roughly half of what reaches the JSON is not a bullet: '# Summary' prose
# becomes basics.summary, entry prose becomes work[].summary /
# projects[].description, and the frontmatter 'label' becomes basics.label —
# the first line a reader sees. Before these tests all of it was invisible to
# the rules and numbers gates.

from cv_lint import _claimed_numbers


def with_entry_prose(prose: str, doc: str = CV) -> str:
    """Give the 'csense' entry a prose paragraph, before its bullet list."""
    return doc.replace("-->\n\n- Drove", f"-->\n\n{prose}\n\n- Drove")


def with_summary(prose: str, doc: str = CV) -> str:
    return doc.replace("Engineer.", prose)


def with_label(label: str, doc: str = CV) -> str:
    return doc.replace('phone = ""', f'phone = ""\nlabel = "{label}"')


def with_fm_summary(summary: str, doc: str = CV) -> str:
    return doc.replace('phone = ""', f'phone = ""\nsummary = "{summary}"')


# 1. the rules gate must read every published string, not just bullets

def test_banned_term_in_entry_prose_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", with_entry_prose("Managed the estate with Terraform."))
    problems = check_rules([f], rules_file(tmp_path))
    assert len(problems) == 1
    assert problems[0].fatal
    assert "Terraform" in problems[0].message


def test_banned_term_in_summary_prose_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", with_summary("Platform engineer fluent in Terraform."))
    problems = check_rules([f], rules_file(tmp_path))
    assert len(problems) == 1
    assert problems[0].fatal
    assert "Terraform" in problems[0].message


def test_banned_term_in_frontmatter_label_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", with_label("Staff Engineer | Terraform"))
    problems = check_rules([f], rules_file(tmp_path))
    assert len(problems) == 1
    assert problems[0].fatal
    # No line number exists for a frontmatter value, so the finding is
    # anchored to line 1 and names the field instead of guessing a line.
    assert problems[0].line == 1
    assert "label" in problems[0].message


def test_banned_term_in_frontmatter_summary_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", with_fm_summary("Ten years of Terraform."))
    problems = check_rules([f], rules_file(tmp_path))
    assert len(problems) == 1
    assert problems[0].line == 1
    assert "summary" in problems[0].message


def test_qualified_term_in_prose_without_its_qualifier_is_fatal(tmp_path):
    f = write(tmp_path, "resume-a", with_summary("Shipped a RAG platform."))
    problems = check_rules([f], rules_file(tmp_path))
    assert problems and problems[0].fatal


def test_qualified_term_in_prose_with_its_qualifier_passes(tmp_path):
    f = write(tmp_path, "resume-a", with_summary("Building a RAG platform (in-progress)."))
    assert check_rules([f], rules_file(tmp_path)) == []


def test_the_adversarial_summary_probe_is_caught(tmp_path):
    # The exact rewrite that used to produce zero findings across all gates.
    f = write(tmp_path, "resume-a", with_summary(
        "Staff platform engineer with 15 years owning Terraform, PySpark and fluent German"))
    rules = load_rules(Path(__file__).parent.parent.parent / "docs" / "resume" / "rules.toml")
    problems = check_rules([f], rules)
    assert len([p for p in problems if p.fatal]) >= 3


# 2. prose numbers need a grounding rule of their own

def test_number_in_entry_prose_absent_from_the_cv_entry_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_entry_prose("Ran a team of 9 engineers."))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "9" in problems[0].message
    assert "csense" in problems[0].message


def test_number_in_entry_prose_grounded_by_a_cv_bullet_passes(tmp_path):
    cv = write(tmp_path, "cv", CV.replace(SOURCE, f"{SOURCE} across 9 teams"))
    f = write(tmp_path, "resume-a", with_entry_prose("Ran a team of 9 engineers."))
    assert check_numbers(cv, [f]) == []


def test_number_in_entry_prose_grounded_by_the_cv_entry_prose_passes(tmp_path):
    cv = write(tmp_path, "cv", with_entry_prose("The group had 9 engineers."))
    f = write(tmp_path, "resume-a", with_entry_prose("Ran a team of 9 engineers."))
    assert check_numbers(cv, [f]) == []


def test_entry_prose_with_no_matching_cv_entry_cannot_be_grounded(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              with_entry_prose("Ran a team of 9 engineers.").replace('id = "csense"',
                                                                     'id = "ghost"'))
    problems = check_numbers(cv, [f])
    assert problems and problems[0].fatal
    assert "ghost" in problems[0].message


def test_number_in_summary_prose_absent_from_cv_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_summary("Platform engineer with 15 years of practice."))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "15" in problems[0].message


def test_number_in_summary_prose_present_anywhere_in_cv_passes(tmp_path):
    # A facet-wide pitch has no single source entry, so the whole of cv.md
    # is its grounding text — here the number comes from a Work bullet.
    cv = write(tmp_path, "cv", CV.replace(SOURCE, f"{SOURCE} over 15 years"))
    f = write(tmp_path, "resume-a", with_summary("Platform engineer with 15 years of practice."))
    assert check_numbers(cv, [f]) == []


def test_number_in_frontmatter_label_absent_from_cv_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_label("Senior Engineer | 15 years"))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert problems[0].line == 1
    assert "15" in problems[0].message


def test_cv_own_prose_is_not_number_checked(tmp_path):
    # cv.md has nothing above it to be grounded against; only facets are
    # passed to this gate, and a cv-only run must stay silent.
    cv = write(tmp_path, "cv", with_summary("Engineer with 15 years and 30TB of logs."))
    assert check_numbers(cv, []) == []


# 3. a number carries its unit into the token

def test_unit_suffixed_metrics_are_claims(tmp_path):
    assert _claimed_numbers("reduced p99 latency to 200ms") == ["200ms"]
    assert _claimed_numbers("processed 30TB of logs daily") == ["30TB"]
    assert _claimed_numbers("served 500GB/day of telemetry") == ["500GB"]
    assert _claimed_numbers("cut memory from 4GB to 1GB") == ["4GB", "1GB"]
    assert _claimed_numbers("sub-10ms p95") == ["10ms"]
    assert _claimed_numbers("finished 3rd in the hackathon") == ["3rd"]


def test_identifiers_are_still_not_claims(tmp_path):
    assert _claimed_numbers("a k3s cluster") == []
    assert _claimed_numbers("a Hetzner CX23 instance") == []
    assert _claimed_numbers("written in Python3") == []
    assert _claimed_numbers("the v1 schema") == []


def test_unit_suffixed_number_absent_from_source_is_fatal(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Cut p99 to 200ms <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert problems and problems[0].fatal
    assert "200ms" in problems[0].message


def test_unit_suffixed_number_present_in_source_passes(tmp_path):
    cv = write(tmp_path, "cv", CV.replace(SOURCE, f"{SOURCE} at 200ms p99"))
    src_hash = fingerprint(f"{SOURCE} at 200ms p99")
    f = write(tmp_path, "resume-a",
              facet(f"- Cut p99 to 200ms <!-- src: csense-h1 @{src_hash} -->"))
    assert check_numbers(cv, [f]) == []


# 4. numbers compare case-insensitively

def test_magnitude_suffix_case_difference_is_not_a_finding(tmp_path):
    cv = write(tmp_path, "cv", CV.replace(SOURCE, f"{SOURCE} for 14K users"))
    src_hash = fingerprint(f"{SOURCE} for 14K users")
    f = write(tmp_path, "resume-a",
              facet(f"- Reached 14k users <!-- src: csense-h1 @{src_hash} -->"))
    assert check_numbers(cv, [f]) == []


def test_the_message_keeps_the_spelling_the_facet_used(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Reached 14k users <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert "14k" in problems[0].message


# 5. spelled-out magnitudes warn, they do not block

def test_spelled_magnitude_absent_from_source_warns(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a",
              facet(f"- Doubled throughput <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert not problems[0].fatal
    assert "doubled" in problems[0].message.lower()


def test_spelled_magnitude_present_in_source_passes(tmp_path):
    cv = write(tmp_path, "cv", CV.replace(SOURCE, "Doubled the GitOps throughput"))
    src_hash = fingerprint("Doubled the GitOps throughput")
    f = write(tmp_path, "resume-a",
              facet(f"- Doubled delivery throughput <!-- src: csense-h1 @{src_hash} -->"))
    assert check_numbers(cv, [f]) == []


def test_spelled_magnitude_in_prose_warns(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_summary("Halved the cost of the platform."))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert not problems[0].fatal
    assert "halved" in problems[0].message.lower()


def test_multiword_spelled_magnitude_warns(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_summary("Cut latency by an order of magnitude."))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert not problems[0].fatal
    assert "order of magnitude" in problems[0].message.lower()
