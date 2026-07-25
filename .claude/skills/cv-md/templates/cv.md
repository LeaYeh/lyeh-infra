+++
# ---------------------------------------------------------------------------
# TEMPLATE — comprehensive CV. Copy to docs/resume/cv.md and replace every
# placeholder. All content below is invented filler, not career data.
#
# TOML `#` comments (here and inside <!--meta --> blocks) are the only inert
# comments in this format. A stray <!-- html comment --> in the body parses as
# PROSE, not as a comment.
#
# Frontmatter becomes JSON Resume `basics`. Allowed keys, and no others:
#   name  label  image  email  phone  url  location  profiles
# `summary` is NOT a frontmatter key — it comes from the `# Summary` section.
# ---------------------------------------------------------------------------
name = "Example Name"
label = "Example Title | Example Focus | Example Specialism"
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

First paragraph of the professional summary. Lines are unwrapped and joined
with a single space, so hard-wrap freely.

Second paragraph. Paragraphs are separated by a blank line and join with a
blank line in the output; the one-page renderer shows only the first.

# Work

## Example Company — Example Position
<!--meta
# `id` is a human handle for this entry. It is never emitted into the JSON;
# it is the prefix of this entry's bullet IDs.
id = "example-co"
# `start` -> startDate (required by the schema), `end` -> endDate.
# Dates are YYYY-MM-DD, or "" for open-ended / present.
start = "2024-01-01"
end = ""
location = "Example City, Country"
url = "https://example.com"
-->

One or two sentences of context about the employer or the mandate. This becomes
`work[].summary`. Prose must come before the bullet list.

- Example achievement stated as an outcome, with a real metric such as 20% {#example-co-h1}
- Example architectural decision and the constraint it was made under {#example-co-h2}
- Example collaboration or ownership statement {#example-co-h3}

## Example Previous Company — Example Previous Position
<!--meta
id = "example-prev"
start = "2020-01-01"
end = "2023-12-01"
location = "Example City, Country"
url = "https://example.com"
-->

Context sentence for the previous role.

- Example earlier achievement {#example-prev-h1}
- Example earlier tooling or platform work {#example-prev-h2}

# Volunteer

## Example Organisation — Example Volunteer Role
<!--meta
id = "example-org"
start = "2023-01-01"
end = "2023-12-01"
url = "https://example.org"
-->

Context sentence about the organisation and the contribution. Becomes
`volunteer[].summary`.

- Example volunteer contribution {#example-org-h1}
- Example second contribution {#example-org-h2}

# Education

## Example University — Example Field of Study
<!--meta
id = "example-uni"
studyType = "Bachelor"
start = "2016-09-01"
end = "2020-06-01"
url = "https://example.edu"
score = ""
-->

- Example Course One
- Example Course Two

# Projects

## example-project — Example Project Subtitle
<!--meta
# Projects headings are a single field, so any number of em dashes stays
# inside the project name.
id = "example-project"
start = "2025-01-01"
end = ""
url = "https://github.com/example/example-project"
roles = ["Author"]
keywords = ["example-keyword", "another-keyword"]
-->

One paragraph describing what the project is and why it exists. Becomes
`projects[].description`.

- Example design decision and the trade-off behind it {#example-project-h1}
- Example component built and what it does {#example-project-h2}
- Example measurable result {#example-project-h3}

## example-second-project — Another Example Project
<!--meta
id = "example-second-project"
start = "2024-03-01"
end = "2024-09-01"
url = "https://github.com/example/example-second-project"
roles = ["Contributor"]
-->

One paragraph describing the second project.

- Example contribution to the second project {#example-second-project-h1}

# Skills

## Example Skill Group
<!--meta
id = "skill-example-group"
level = "Advanced"
-->

- Example Tool
- Example Practice
- Example Technology

## Example Second Skill Group
<!--meta
id = "skill-example-second-group"
level = "Intermediate"
-->

- Example Language
- Example Library

# Awards

## Example Award Title
<!--meta
id = "example-award"
date = "2022-12-01"
awarder = "Example Awarding Body"
-->

One sentence on what the award recognised. Becomes `awards[].summary`.

# Certificates

## Example Certification Name
<!--meta
id = "example-cert"
date = "2024-04-01"
issuer = "Example Issuer"
url = "https://example.com/credential/000000"
-->

# Publications

## Example Publication Title
<!--meta
# Publications take no prose paragraph, so the abstract goes in `summary` here.
id = "example-publication"
publisher = "Example Publisher"
releaseDate = "2020-06-01"
url = "https://example.com/publication"
summary = "One-sentence description of the publication."
-->

# Languages

## Example Language One
<!--meta
id = "example-language-one"
fluency = "Native Speaker"
-->

## Example Language Two
<!--meta
id = "example-language-two"
fluency = "Professional Working Proficiency"
-->

# Interests

## Example Interest
<!--meta
id = "example-interest"
-->

- Example Interest Keyword
- Another Interest Keyword

# References

## Example Referee Name
<!--meta
id = "example-reference"
-->

The referee's statement goes here as prose; it becomes `references[].reference`.
