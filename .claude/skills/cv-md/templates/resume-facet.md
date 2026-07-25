+++
# ---------------------------------------------------------------------------
# TEMPLATE — one-page facet resume. Copy to docs/resume/resume-<a|b|c>.md
# and replace every placeholder. All content below is invented filler.
#   a = Platform / Infrastructure / SRE
#   b = Data Engineer
#   c = MLOps / AI Platform
#
# INVARIANTS — copied VERBATIM from cv.md, never tailored per facet:
#   * this whole frontmatter except `label`: name, image, email, phone,
#     url, [location], [[profiles]]
#   * every Work entry's heading (company — position) and its meta
#     `start`, `end`, `location`
#   * the entire Education section, entry for entry, course for course
#   * the entire Languages section
# `make cv-lint` compares these against cv.md and fails on any drift.
#
# TAILORABLE: `label`, the Summary prose, each work entry's prose and bullets,
# which work entries you include, and the Projects / Skills sections.
#
# ANCHORS — every Work / Volunteer / Projects bullet must end with
#   <!-- src: <cv-bullet-id> @<4-lowercase-hex> -->
# citing the cv.md bullet it is a reframing of. Compute the hash with:
#   python3 -c "
#   import sys; sys.path.insert(0, 'scripts')
#   from cv_lint import cv_index, CV_MD
#   from resume_md import fingerprint
#   idx, _ = cv_index(CV_MD); print(fingerprint(idx['example-co-h1']))"
# The placeholder hashes below are filler and will not match anything.
# ---------------------------------------------------------------------------
name = "Example Name"
label = "Example Title | Example Facet Angle"
image = "https://example.com/avatar.png"
email = "example@example.com"
phone = ""
url = "https://example.com"

[location]
countryCode = "AT"
address = "Example Street 1"
postalCode = "1010"
city = "Example City"
region = ""

[[profiles]]
network = "LinkedIn"
username = "example"
url = "https://www.linkedin.com/in/example/"

[[profiles]]
network = "GitHub"
username = "example"
url = "https://github.com/example"
+++

# Summary

Three or four sentences pitching this facet only. Name the concrete stack and
the scale, drop everything the target audience does not care about. The one-page
renderer shows the first paragraph, so keep it to one.

# Work

## Example Company — Example Position
<!--meta
# heading + start/end/location are invariant: copied verbatim from cv.md
id = "example-co"
start = "2024-01-01"
end = ""
location = "Example City, Country"
url = "https://example.com"
-->

One sentence of employer context, reframed toward this facet.

- Example achievement reframed for this facet, keeping the 20% from the source <!-- src: example-co-h1 @a1b2 -->
- Example architectural decision, reframed <!-- src: example-co-h2 @c3d4 -->

## Example Previous Company — Example Previous Position
<!--meta
id = "example-prev"
start = "2020-01-01"
end = "2023-12-01"
location = "Example City, Country"
url = "https://example.com"
-->

One sentence of context for the previous role.

- Example earlier achievement, reframed for this facet <!-- src: example-prev-h1 @e5f6 -->

# Skills

## Example Facet Skill Group
<!--meta
id = "skill-example-facet"
level = "Advanced"
-->

- Example Tool
- Example Practice
- Example Technology

## Example Supporting Skill Group
<!--meta
id = "skill-example-supporting"
level = "Intermediate"
-->

- Example Language
- Example Library

# Projects

## example-project — Example Project Subtitle
<!--meta
id = "example-project"
start = "2025-01-01"
end = ""
url = "https://github.com/example/example-project"
roles = ["Author"]
-->

One paragraph on the project, angled at this facet.

- Example design decision, reframed <!-- src: example-project-h1 @0a1b -->
- Example measurable result <!-- src: example-project-h3 @2c3d -->

# Education

## Example University — Example Field of Study
<!--meta
# invariant: this entry must match cv.md exactly, courses included
id = "example-uni"
studyType = "Bachelor"
start = "2016-09-01"
end = "2020-06-01"
url = "https://example.edu"
score = ""
-->

- Example Course One
- Example Course Two

# Languages

## Example Language One
<!--meta
# invariant: the whole Languages section must match cv.md exactly
id = "example-language-one"
fluency = "Native Speaker"
-->

## Example Language Two
<!--meta
id = "example-language-two"
fluency = "Professional Working Proficiency"
-->
