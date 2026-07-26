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


def test_drifting_start_date_is_reported(tmp_path):
    # Employment dates are the invariant a tailored facet is most tempted to
    # round: each one is checked on its own, not just the employer name.
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a",
                  CV.replace('start = "2024-08-01"', 'start = "2023-08-01"'))
    assert any("work" in p.message for p in check_invariants(cv, [facet]))


def test_drifting_end_date_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a", CV.replace('end = ""', 'end = "2026-01-01"'))
    assert any("work" in p.message for p in check_invariants(cv, [facet]))


def test_drifting_work_location_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV)
    facet = write(tmp_path, "resume-a",
                  CV.replace('location = "Vienna, Austria"', 'location = "Berlin, Germany"'))
    assert any("work" in p.message for p in check_invariants(cv, [facet]))


CV_EDUCATION = CV.replace("# Languages", '''# Education

## National Taiwan University — Computer Science

- Operating Systems
- Distributed Systems

# Languages''')


def test_matching_education_passes(tmp_path):
    cv = write(tmp_path, "cv", CV_EDUCATION)
    facet = write(tmp_path, "resume-a", CV_EDUCATION)
    assert check_invariants(cv, [facet]) == []


def test_drifting_education_area_is_reported(tmp_path):
    # A degree is a fact about the world, not a facet's pitch — an 'area'
    # reworded to match the JD is a fabricated credential.
    cv = write(tmp_path, "cv", CV_EDUCATION)
    facet = write(tmp_path, "resume-a",
                  CV_EDUCATION.replace("Computer Science", "Electrical Engineering"))
    assert any("education" in p.message for p in check_invariants(cv, [facet]))


def test_drifting_education_institution_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV_EDUCATION)
    facet = write(tmp_path, "resume-a",
                  CV_EDUCATION.replace("National Taiwan University", "Stanford University"))
    assert any("education" in p.message for p in check_invariants(cv, [facet]))


def test_invented_education_course_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV_EDUCATION)
    facet = write(tmp_path, "resume-a",
                  CV_EDUCATION.replace("- Distributed Systems", "- Machine Learning"))
    assert any("education" in p.message for p in check_invariants(cv, [facet]))


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


def test_a_violation_below_a_clean_bullet_is_still_found(tmp_path):
    # The gate has to read the whole bullet list, not the first bullet: an
    # assistant appending a claim to an entry writes it at the bottom.
    f = write(tmp_path, "resume-a", facet(
        "- Owned the GitOps delivery path\n- Managed infra with Terraform"))
    problems = check_rules([f], rules_file(tmp_path))
    assert len(problems) == 1
    assert problems[0].fatal
    assert problems[0].line == 22          # the second bullet, not the first
    assert "Terraform" in problems[0].message


def test_every_bullet_after_the_first_is_read(tmp_path):
    f = write(tmp_path, "resume-a", facet(
        "- Owned the GitOps delivery path\n"
        "- Managed infra with Terraform\n"
        "- Built a RAG pipeline"))
    problems = check_rules([f], rules_file(tmp_path))
    assert [p.line for p in problems] == [22, 23]


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


def test_a_number_in_the_source_does_not_license_a_different_number(tmp_path):
    # Grounding is membership, not "the source has some number, so any number
    # is fine". Every other failing-numbers case here uses a source with no
    # digits at all, which cannot tell those two rules apart: with a source of
    # '12 services' the facet's '30' must still be fatal.
    cv_text = CV.replace(SOURCE, f"{SOURCE} for 12 services")
    cv = write(tmp_path, "cv", cv_text)
    src_hash = fingerprint(f"{SOURCE} for 12 services")
    f = write(tmp_path, "resume-a",
              facet(f"- Migrated 30 services <!-- src: csense-h1 @{src_hash} -->"))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "number(s) 30 do not appear" in problems[0].message


def test_only_the_ungrounded_number_of_a_mixed_bullet_is_reported(tmp_path):
    # The facet keeps the grounded '12' and invents '30'; only '30' is a finding.
    cv_text = CV.replace(SOURCE, f"{SOURCE} for 12 services")
    cv = write(tmp_path, "cv", cv_text)
    src_hash = fingerprint(f"{SOURCE} for 12 services")
    f = write(tmp_path, "resume-a",
              facet(f"- Migrated 12 of 30 services <!-- src: csense-h1 @{src_hash} -->"))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert "number(s) 30 do not appear" in problems[0].message


def test_a_number_in_the_cv_at_large_does_not_license_a_prose_number(tmp_path):
    # Same rule for the whole-document grounding path used by section prose.
    cv = write(tmp_path, "cv", CV.replace(SOURCE, f"{SOURCE} over 15 years"))
    f = write(tmp_path, "resume-a", with_summary("Platform engineer with 20 years of practice."))
    problems = check_numbers(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "number(s) 20 do not appear" in problems[0].message


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


def _rebuild_then_edit_json(tmp_path, md, mutate):
    """Build ``md``, then hand-edit the committed JSON so it no longer matches."""
    build_file(md)
    out = md.with_suffix(".json")
    data = json.loads(out.read_text())
    mutate(data)
    out.write_text(json.dumps(data))
    return out


def test_json_drifting_outside_basics_name_is_fatal(tmp_path):
    # Freshness is equality of the whole document. A committed JSON that keeps
    # the name but has a hand-edited job title is exactly the drift that ships
    # a lie — comparing any single field would wave it through.
    md = write(tmp_path, "cv", CV)

    def bump_title(data):
        data["work"][0]["position"] = "Principal Software Engineer"

    _rebuild_then_edit_json(tmp_path, md, bump_title)
    problems = check_freshness([md])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "cv-build" in problems[0].message


def test_json_drifting_in_a_bullet_is_fatal(tmp_path):
    md = write(tmp_path, "cv", CV)

    def inflate_highlight(data):
        data["work"][0]["highlights"][0] = "Drove the GitOps migration for 40 teams"

    _rebuild_then_edit_json(tmp_path, md, inflate_highlight)
    assert [p.fatal for p in check_freshness([md])] == [True]


def test_json_drifting_in_a_contact_field_is_fatal(tmp_path):
    md = write(tmp_path, "cv", CV)

    def repoint_email(data):
        data["basics"]["email"] = "someone-else@example.com"

    _rebuild_then_edit_json(tmp_path, md, repoint_email)
    assert [p.fatal for p in check_freshness([md])] == [True]


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


# --- 6. a citation must point at the entry it sits in -------------------
#
# A valid, fresh anchor proves the cited bullet exists and is unchanged. It
# proves nothing about *relevance*: a MediaTek achievement cited under the
# c-sense entry used to pass every gate. Bullet IDs are '<entry-id>-h<n>', so
# the cited bullet's owning entry must be the citing bullet's own entry.

MT_SOURCE = "Built a monitoring & alerting stack for PB-scale data and ML systems"
MT_BULLET = f"- {MT_SOURCE} {{#mediatek-de-h3}}"

CV_TWO_ENTRIES = CV.replace("# Languages", f'''## MediaTek — Senior Engineer
<!--meta
id = "mediatek-de"
start = "2019-01-01"
end = "2024-07-31"
location = "Hsinchu, Taiwan"
-->

{MT_BULLET}

# Languages''')


def facet2(csense_bullet: str) -> str:
    """Two-entry facet: c-sense takes ``csense_bullet``, MediaTek keeps a valid anchor."""
    return CV_TWO_ENTRIES.replace(
        "- Drove the GitOps migration {#csense-h1}", csense_bullet,
    ).replace(
        MT_BULLET,
        f"- Ran the monitoring stack <!-- src: mediatek-de-h3 @{fingerprint(MT_SOURCE)} -->",
    )


def test_same_entry_citations_pass(tmp_path):
    cv = write(tmp_path, "cv", CV_TWO_ENTRIES)
    f = write(tmp_path, "resume-a", facet2(
        f"- Owned the GitOps delivery path <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    assert check_provenance(cv, [f]) == []


def test_cross_entry_citation_is_fatal(tmp_path):
    # The measured probe: a MediaTek achievement re-filed under c-sense with a
    # live, current anchor.
    cv = write(tmp_path, "cv", CV_TWO_ENTRIES)
    f = write(tmp_path, "resume-a", facet2(
        f"- {MT_SOURCE} <!-- src: mediatek-de-h3 @{fingerprint(MT_SOURCE)} -->"))
    problems = check_provenance(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal
    assert "mediatek-de-h3" in problems[0].message
    assert "'mediatek-de'" in problems[0].message
    assert "'csense'" in problems[0].message


def test_cross_entry_citation_is_caught_even_when_stale(tmp_path):
    cv = write(tmp_path, "cv", CV_TWO_ENTRIES)
    f = write(tmp_path, "resume-a", facet2(
        "- Ran a monitoring stack <!-- src: mediatek-de-h3 @dead -->"))
    problems = check_provenance(cv, [f])
    assert len(problems) == 1
    assert problems[0].fatal


CV_HYPHENATED = CV.replace('id = "csense"', 'id = "42-vienna-tutor"').replace(
    "{#csense-h1}", "{#42-vienna-tutor-h1}")


def test_hyphenated_entry_id_is_not_split_on_hyphens(tmp_path):
    # Splitting '42-vienna-tutor-h1' on '-' yields '42', not the entry id.
    # The owning entry has to come from the cv.md tree, not from the string.
    cv = write(tmp_path, "cv", CV_HYPHENATED)
    f = write(tmp_path, "resume-a", CV_HYPHENATED.replace(
        "- Drove the GitOps migration {#42-vienna-tutor-h1}",
        f"- Owned the GitOps path <!-- src: 42-vienna-tutor-h1 @{fingerprint(SOURCE)} -->"))
    assert check_provenance(cv, [f]) == []


def test_citation_from_an_entry_without_an_id_is_fatal(tmp_path):
    # An entry with no meta 'id' cannot own any bullet, so it cannot cite one.
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", facet(GOOD_ANCHOR).replace('id = "csense"\n', ""))
    problems = check_provenance(cv, [f])
    assert problems and problems[0].fatal
    assert "csense-h1" in problems[0].message


# --- 7. contact and attribution fields are invariants -------------------

CV_CONTACT = CV.replace('phone = ""', '''phone = ""
url = "https://leayeh.example"
image = "https://example.com/avatar.png"

[[profiles]]
network = "LinkedIn"
username = "Lea Yeh"
url = "https://www.linkedin.com/in/lea-yeh/"

[[profiles]]
network = "GitHub"
username = "LeaYeh"
url = "https://github.com/LeaYeh"
''')


def test_matching_contact_and_attribution_fields_pass(tmp_path):
    cv = write(tmp_path, "cv", CV_CONTACT)
    f = write(tmp_path, "resume-a", CV_CONTACT)
    assert check_invariants(cv, [f]) == []


def test_drifting_profile_url_is_reported(tmp_path):
    # The probe: a facet's LinkedIn profile repointed at a stranger.
    cv = write(tmp_path, "cv", CV_CONTACT)
    f = write(tmp_path, "resume-a", CV_CONTACT.replace("in/lea-yeh/", "in/a-stranger/"))
    problems = check_invariants(cv, [f])
    assert any("basics" in p.message for p in problems)


def test_dropping_a_profile_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV_CONTACT)
    f = write(tmp_path, "resume-a", CV_CONTACT.replace('''
[[profiles]]
network = "GitHub"
username = "LeaYeh"
url = "https://github.com/LeaYeh"
''', "\n"))
    assert any("basics" in p.message for p in check_invariants(cv, [f]))


def test_drifting_basics_url_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV_CONTACT)
    f = write(tmp_path, "resume-a", CV_CONTACT.replace(
        "https://leayeh.example", "https://www.google.com/"))
    assert any("basics" in p.message for p in check_invariants(cv, [f]))


def test_drifting_image_is_reported(tmp_path):
    cv = write(tmp_path, "cv", CV_CONTACT)
    f = write(tmp_path, "resume-a", CV_CONTACT.replace(
        "https://example.com/avatar.png", "https://example.com/someone-else.png"))
    assert any("basics" in p.message for p in check_invariants(cv, [f]))


CV_WORK_URL = CV.replace(
    'location = "Vienna, Austria"',
    'location = "Vienna, Austria"\nurl = "https://www.c-sense.at/"')


def test_drifting_work_url_is_reported(tmp_path):
    # The probe: work[0].url repointed at an unrelated site.
    cv = write(tmp_path, "cv", CV_WORK_URL)
    f = write(tmp_path, "resume-a", CV_WORK_URL.replace(
        "https://www.c-sense.at/", "https://www.google.com/"))
    assert any("work" in p.message for p in check_invariants(cv, [f]))


def test_label_stays_tailorable(tmp_path):
    # basics.label is the facet's pitch, not an invariant — the rules and
    # numbers gates cover it instead.
    cv = write(tmp_path, "cv", with_label("Senior Software Engineer"))
    f = write(tmp_path, "resume-a", with_label("Data Engineer"))
    assert check_invariants(cv, [f]) == []


def test_summaries_stay_tailorable(tmp_path):
    cv = write(tmp_path, "cv", with_summary("A broad engineer."))
    f = write(tmp_path, "resume-a", with_summary("A platform engineer."))
    assert check_invariants(cv, [f]) == []


def test_work_summary_stays_tailorable(tmp_path):
    cv = write(tmp_path, "cv", with_entry_prose("Ran the platform team."))
    f = write(tmp_path, "resume-a", with_entry_prose("Built the delivery path."))
    assert check_invariants(cv, [f]) == []


# --- 8. a prose finding says which line it is anchored to ---------------
#
# The parser records a line for the '# Summary' heading but not for the
# paragraph beneath it, so a prose finding is reported two-or-more lines above
# the text the operator has to edit. Until the tree carries a prose line, the
# message has to say so.

SUMMARY_HEADING_LINE = 7   # CV: '+++', name, email, phone, '+++', '', '# Summary'


def test_section_prose_finding_names_the_heading_it_is_anchored_to(tmp_path):
    cv = write(tmp_path, "cv", CV)
    f = write(tmp_path, "resume-a", with_summary("Platform engineer with 15 years."))
    problems = check_numbers(cv, [f])
    assert problems[0].line == SUMMARY_HEADING_LINE
    assert "heading" in problems[0].message
    assert "Summary" in problems[0].message


def test_entry_prose_finding_names_the_heading_it_is_anchored_to(tmp_path):
    f = write(tmp_path, "resume-a", with_entry_prose("Managed the estate with Terraform."))
    problems = check_rules([f], rules_file(tmp_path))
    assert "heading" in problems[0].message
    assert "c-sense GmbH" in problems[0].message


def test_bullet_findings_carry_no_anchor_caveat(tmp_path):
    # A bullet's line is the bullet's own line; nothing to disclaim.
    f = write(tmp_path, "resume-a", facet("- Managed infra with Terraform"))
    problems = check_rules([f], rules_file(tmp_path))
    assert "heading" not in problems[0].message


# --- 9. --strict makes warnings fatal on the publishing paths -----------

import cv_lint


def corpus(tmp_path, monkeypatch, facet_text, cv_text=CV):
    """A self-contained resume set, wired up as cv_lint's RESUME_DIR."""
    cv = write(tmp_path, "cv", cv_text)
    f = write(tmp_path, "resume-a", facet_text)
    build_file(cv)
    build_file(f)
    monkeypatch.setattr(cv_lint, "RESUME_DIR", tmp_path)
    monkeypatch.setattr(cv_lint, "CV_MD", cv)
    monkeypatch.setattr(cv_lint, "RULES_FILE", tmp_path / "no-rules.toml")
    return cv, f


def test_clean_corpus_passes_in_both_modes(tmp_path, monkeypatch):
    corpus(tmp_path, monkeypatch, facet(GOOD_ANCHOR))
    assert cv_lint.main([]) == 0
    assert cv_lint.main(["--strict"]) == 0


def test_stale_anchor_passes_by_default_but_blocks_under_strict(tmp_path, monkeypatch):
    # The measured probe: a gutted cv.md bullet leaves the facet claim intact,
    # cv-lint says rc=0, and `make cv-publish` ships it anyway.
    corpus(tmp_path, monkeypatch, facet("- Owned the GitOps delivery path "
                                        "<!-- src: csense-h1 @dead -->"))
    assert cv_lint.main([]) == 0
    assert cv_lint.main(["--strict"]) == 1


def test_spelled_magnitude_warning_also_blocks_under_strict(tmp_path, monkeypatch):
    corpus(tmp_path, monkeypatch,
           facet(f"- Doubled throughput <!-- src: csense-h1 @{fingerprint(SOURCE)} -->"))
    assert cv_lint.main([]) == 0
    assert cv_lint.main(["--strict"]) == 1


def test_a_fatal_problem_fails_in_both_modes(tmp_path, monkeypatch):
    corpus(tmp_path, monkeypatch, facet("- Owned the GitOps delivery path"))
    assert cv_lint.main([]) == 1
    assert cv_lint.main(["--strict"]) == 1


def test_unknown_flag_is_rejected(tmp_path, monkeypatch):
    corpus(tmp_path, monkeypatch, facet(GOOD_ANCHOR))
    assert cv_lint.main(["--publish"]) == 2
