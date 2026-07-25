# The resume Markdown grammar

Authority: `scripts/resume_md.py` (syntax) and `scripts/jsonresume_map.py`
(semantics). This document describes what those two files actually accept. If
they ever disagree with this page, the code wins.

A document is: one `+++` TOML frontmatter block, then a sequence of
`# Section` headings, each holding `## Entry` headings, each holding an optional
`<!--meta` block, optional prose, and an optional bullet list.

---

## 1. Frontmatter — `+++ … +++`

The document **must** start with a `+++` fence on line 1. Everything between the
fences is TOML, and it becomes JSON Resume `basics`.

```toml
+++
name = "Example Name"
label = "Example Job Title | Focus Area"
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
network = "GitHub"
username = "example"
url = "https://github.com/example"
+++
```

**The only allowed keys** (`BASICS_KEYS` in `jsonresume_map.py`):

```
name  label  image  email  phone  url  location  profiles
```

Any other key is a hard error: `unknown frontmatter key(s): …`, reported at
line 1.

Notes:

- `summary` is **not** a frontmatter key. `basics.summary` comes from the
  `# Summary` section (see §2).
- `name` and `email` are required by the schema gate.
- `location` is a TOML table; its allowed keys are `address`, `postalCode`,
  `city`, `countryCode`, `region`.
- `profiles` is an array of tables (`[[profiles]]`); each needs at least
  `network`, and may carry `username` and `url`.
- A TOML syntax error is reported at the offending source line (on Python 3.14+;
  older interpreters fall back to line 1).
- **TOML `#` comments inside the frontmatter are the only truly inert comments
  in this format.** Put editorial notes there — see §9.

---

## 2. `# Section` headings

A line beginning with `# ` opens a section. The title must be one of:

```
Summary  Work  Volunteer  Education  Projects  Skills
Awards   Certificates  Publications  Languages  Interests  References
```

Anything else is an error: `unknown section '<title>'`.

`# Summary` is special: it takes **no entries**, only prose, and that prose
becomes `basics.summary`.

```markdown
# Summary

First paragraph of the professional summary.

Second paragraph, joined to the first with a blank line.
```

Every other section takes only `## ` entries. Prose written directly under a
non-`Summary` section heading is parsed without error but is **silently dropped**
by the mapper — do not put content there.

---

## 3. `## Entry` headings

A line beginning with `## ` opens an entry inside the current section. The
heading text is split on the em dash `—` (U+2014) into the fields that section
expects:

```markdown
## Example Company — Example Position          <- Work: name — position
## Example University — Example Field          <- Education: institution — area
## example-project — Example Subtitle          <- Projects: the whole line is `name`
```

**The split consumes only the separators it needs** — `maxsplit` is
`len(fields) - 1`. So:

- A one-field section (Projects, Skills, Awards, …) keeps every em dash inside
  the single field: `## lyeh-infra — Self-Hosted Kubernetes Infrastructure` is
  one project name.
- A two-field section splits on the **first** em dash only; later ones stay in
  the second field: `## 42 Vienna — Computer Science — Software Architecture`
  is institution `42 Vienna`, area `Computer Science — Software Architecture`.

Residual limitation to know about: for a two-field section this is "first em
dash wins", so an em dash inside the *first* field would mis-split. Don't put
one there.

Wrong field count is an error naming the expected shape:
`'Work' heading must be: <name> — <position>`.

An entry before any `# Section` heading is an error, as is a bullet or prose
before the first section heading.

---

## 4. The `<!--meta … -->` block

Structured fields that are not the heading, the prose, or the bullets go in a
meta block immediately after the entry heading. The body is TOML.

```markdown
## Example Company — Example Position
<!--meta
id = "example-co"
start = "2024-01-01"
end = ""
location = "Example City, Country"
url = "https://example.com"
-->
```

Deliberate rules the parser enforces:

- **`<!--meta` must stand alone on its opening line.** A line that merely starts
  with `<!--meta` — `<!--metadata …`, `<!--meta id = "x"` — is an error, not
  prose: `the <!--meta marker must stand alone on its line; put the TOML on the
  following lines`. Freeform HTML comments are not part of this grammar, so the
  parser refuses to guess.
- **At most one meta block per entry.** A second one is
  `multiple meta blocks in '<heading>'`. Silently merging or overwriting would
  lose data.
- A meta block before any `## ` entry is
  `meta block must follow a '## ' entry heading`.
- The closing `-->` must be alone on its line; otherwise
  `unterminated <!--meta block`, reported at the opening line.
- TOML errors inside the block are reported at the offending line.

`id` is a special key: it is a **human-facing handle for the entry** and is
never emitted into the JSON. Everything else is copied through, with two
aliases:

| Meta key | JSON Resume field |
|---|---|
| `start` | `startDate` |
| `end`   | `endDate` |

Dates must be `YYYY-MM-DD` or the empty string `""` (used for "present"/unknown).
Anything else fails the schema gate:
`must be YYYY-MM-DD or empty, got '2024'`.

Which meta keys each section accepts is in `references/jsonresume-mapping.md`.

---

## 5. Prose

Any non-blank line that is not a heading, a bullet, or a meta marker is prose.
Consecutive lines are unwrapped and joined with a single space, so you may hard-wrap
freely in the source.

```markdown
## Example Company — Example Position
<!--meta
id = "example-co"
start = "2024-01-01"
-->

Example Company builds example things for example customers.
This sentence continues the same paragraph.

- First achievement {#example-co-h1}
```

produces `work[0].summary = "Example Company builds example things for example
customers. This sentence continues the same paragraph."`

**Multiple paragraphs** — separate them with a blank line in the source; they
join with `"\n\n"`:

```markdown
# Summary

First paragraph.

Second paragraph.
```

→ `basics.summary = "First paragraph.\n\nSecond paragraph."`

That is the paragraph break JSON Resume string fields may legitimately contain:
the one-page renderer takes the first paragraph; the full renderer emits one
`<p>` per paragraph.

**Prose must come before the bullet list.** A paragraph flushed after bullets
have already been recorded is a hard error —
`prose must come before the bullet list in '<heading>'` — because under naive
joining it would be silently appended to the entry's summary and no one would
notice.

Sections whose spec has no prose field (Education, Skills, Certificates,
Publications, Languages, Interests) reject prose entirely:
`'Education' entries take no prose paragraph`.

---

## 6. Bullets

A bullet is a line matching `^-\s+(.+?)\s*$`: a `-`, at least one space or tab,
then the text. `*` and `+` markers are **not** bullets — they parse as prose.

```markdown
- Placeholder achievement with a measurable outcome {#example-co-h1}
```

A bullet outside an entry is an error
(`bullet in section '<title>' has no '## ' entry`).

Sections whose spec has no bullet field (Awards, Certificates, Publications,
Languages, References) reject bullets:
`'Awards' entries take no bullet list`.

---

## 7. The two bullet annotations

A bullet may carry **at most one of each**, at the end of the line, in either
order. Both are stripped before the text is stored, fingerprinted, or rendered.

### `{#id}` — declares a source bullet (CV only)

```markdown
- Placeholder achievement with a measurable outcome {#example-co-h1}
```

Regex: `\s*\{#([A-Za-z0-9._-]+)\}$` — letters, digits, `.`, `_`, `-`.

Allowed only in sections whose bullets become highlight objects: **Work**,
**Volunteer**, **Projects**. An `{#id}` on an Education course or a Skills
keyword is an error:
`'Skills' bullets must not carry a {#id}`.

### `<!-- src: id @hash -->` — cites a source bullet (facets only)

```markdown
- Reframed version of that achievement <!-- src: example-co-h1 @a1b2 -->
```

Regex: `\s*<!--\s*src:\s*([A-Za-z0-9._-]+)\s*@([0-9a-f]{4})\s*-->$`

The hash is **exactly four lowercase hex characters**. Uppercase, three
characters, or five will not match the annotation at all — the parser will then
see a bullet whose text ends in `-->` and reject it as
`malformed bullet annotation: the only annotations a bullet may carry are
'{#some-id}' and '<!-- src: some-id @abcd -->' (hash is exactly 4 lowercase hex
characters)`. That hard error exists so a typo'd anchor never survives into the
PDF while the provenance gate reports "no source anchor" at a line that visibly
has one.

Both annotations on one bullet is legal (either order) — useful if a facet
bullet is itself a source for something:

```markdown
- Text {#some-id} <!-- src: other-id @a1b2 -->
- Text <!-- src: other-id @a1b2 --> {#some-id}
```

---

## 8. Bullet IDs and fingerprints

### Naming convention

```
<entry-id>-h<n>
```

where `<entry-id>` is the `id` from that entry's meta block and `<n>` is the
1-based position of the bullet in the entry. Real examples: `csense-h3`,
`mediatek-de-h1`, `lyeh-infra-h5`.

The convention is not machine-enforced — the only hard rule is that IDs are
unique within `cv.md` (`duplicate bullet ID '<id>'`). Follow it anyway: it makes
a dangling anchor readable at a glance.

When you insert a bullet in the middle of an entry, **do not renumber the
existing ones.** Every facet anchor pointing at them would break. Append the new
bullet with the next free number instead.

### Computing a fingerprint

The `@hash` is the first 4 hex characters of the SHA-256 of the
whitespace-normalised **bullet text** — that is, after `{#id}` and
`<!-- src: … -->` have been stripped. Fingerprinting the raw Markdown line would
make every anchor mismatch.

From the repo root, look up a CV bullet by ID and print its current fingerprint:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from cv_lint import cv_index, CV_MD
from resume_md import fingerprint
idx, _ = cv_index(CV_MD)
print(fingerprint(idx['csense-h3']))"
# d85d
```

Or fingerprint an arbitrary string:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from resume_md import fingerprint
print(fingerprint('Some bullet text without annotations'))"
```

Whitespace is normalised, so re-wrapping a line does not change its hash; a
single reworded word does.

---

## 9. Comments

There is no comment syntax in the body. A line starting with `<!--` that is not
exactly `<!--meta` is treated as **prose**, which means it may end up in a
summary or description field.

Put editorial notes where they are inert:

- as `#` TOML comments inside the `+++` frontmatter, or
- as `#` TOML comments inside a `<!--meta … -->` block.

---

## 10. Error message quick index

| Message | Cause |
|---|---|
| `document must start with a +++ frontmatter fence` | Missing or misplaced opening fence |
| `unterminated +++ frontmatter fence` | No closing `+++` |
| `frontmatter TOML error: …` | Bad TOML in the frontmatter |
| `unknown frontmatter key(s): …` | Key outside `BASICS_KEYS` |
| `the <!--meta marker must stand alone on its line; …` | Content on the `<!--meta` line |
| `unterminated <!--meta block` | No closing `-->` on its own line |
| `meta TOML error: …` | Bad TOML in a meta block |
| `meta block must follow a '## ' entry heading` | Meta before any entry |
| `multiple meta blocks in '<heading>'` | Two meta blocks in one entry |
| `unknown section '<title>'` | `# Heading` not in the section list |
| `'## ' entry found before any '# Section' heading` | Entry before a section |
| `bullet found before any '# Section' heading` | Bullet before a section |
| `bullet in section '<title>' has no '## ' entry` | Bullet directly under a section heading |
| `prose found before the first '# Section' heading` | Text between frontmatter and first section |
| `prose must come before the bullet list in '<name>'` | Paragraph after bullets |
| `malformed bullet annotation: …` | Annotation that does not match the regexes |
| `'<Section>' heading must be: <a> — <b>` | Wrong number of em-dash-separated fields |
| `'<Section>' entries take no prose paragraph` | Prose in a section with no prose field |
| `'<Section>' entries take no bullet list` | Bullets in a section with no bullet field |
| `'<Section>' bullets must not carry a {#id}` | `{#id}` outside Work/Volunteer/Projects |
