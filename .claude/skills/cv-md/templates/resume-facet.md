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
#     url, [location], [[profiles]]   (image/url/profiles are attribution —
#     pointing them elsewhere claims a different person's identity)
#   * every Work entry's heading (company — position) and its meta
#     `start`, `end`, `location`, `url`
#   * the entire Education section, entry for entry, course for course
#   * the entire Languages section
# `make cv-lint` compares these against cv.md and fails on any drift.
#
# THE WORK LIST IS COMPARED POSITIONALLY, AS A WHOLE LIST. A facet must carry
# the SAME NUMBER of Work entries as cv.md, in the same order. Dropping the
# oldest job to reach one page is the obvious way to compress and it does not
# work: it fails as "'work' drifts from cv.md". Shorten a role instead — its
# prose and its bullets are yours to cut, down to a heading + meta + one bullet.
#
# TAILORABLE: `label`, the Summary prose, each work entry's prose and bullets,
# and the Projects / Skills sections.
#
# ANCHORS — every Work / Volunteer / Projects bullet must end with
#   <!-- src: <cv-bullet-id> @<4-lowercase-hex> -->
# citing the cv.md bullet it is a reframing of, AND that bullet must belong to
# the SAME entry: citing another employer's bullet is fatal, anchor or no
# anchor. Compute the hash with:
#   python3 -c "
#   import sys; sys.path.insert(0, 'scripts')
#   from cv_lint import cv_index, CV_MD
#   from resume_md import fingerprint
#   idx, _ = cv_index(CV_MD); print(fingerprint(idx['example-co-h1']))"
# The placeholder hashes below are filler and will not match anything.
#
# PROSE AND `label` ARE GATED TOO — they are not a soft zone. The rules gate
# reads `label`, the Summary prose and every entry's prose; the numbers gate
# grounds an entry's prose against the cv.md entry with the same meta `id`,
# and the Summary prose and `label` against the whole of cv.md.
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
renderer shows the first paragraph, so keep it to one. Any number here must
already appear somewhere in cv.md — this paragraph is grounded against the whole
document, not against one entry.

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

One sentence of employer context, reframed toward this facet. Numbers here are
grounded against the cv.md entry whose meta `id` is also "example-co".

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
