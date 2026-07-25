# Markdown → JSON Resume mapping

Authority: the `SECTIONS` table in `scripts/jsonresume_map.py` and the field
spec in `scripts/jsonresume_schema.py`.

## The shape of a built document

```json
{
  "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
  "basics":  { ...frontmatter..., "summary": "...from the # Summary section..." },
  "work": [], "volunteer": [], "education": [], "projects": [], "skills": [],
  "awards": [], "certificates": [], "publications": [], "languages": [],
  "interests": [], "references": [],
  "meta": {
    "version": "v1.0.0",
    "canonical": "https://github.com/jsonresume/resume-schema/blob/v1.0.0/schema.json"
  }
}
```

`$schema` and `meta` are **constants injected by the builder**. They are not in
the Markdown and must not be added to it.

Every section key is pre-seeded with `[]`, so **an omitted section becomes an
empty list**, not a missing key. Deleting `# Interests` from a document is safe.

`basics` is the frontmatter filtered to `BASICS_KEYS`, plus `summary` from the
`# Summary` section. `# Summary` is handled before the `SECTIONS` lookup, so it
has no spec row and takes no `## ` entries.

## The section table

For each `# Section`: its JSON key, what the `## ` heading splits into (on the
first `len(fields) - 1` em dashes), where the prose paragraph goes, where the
bullets go, and whether a bullet may carry `{#id}`.

| `# Section` | JSON key | Heading splits into | Prose → | Bullets → | `{#id}` allowed? |
|---|---|---|---|---|---|
| `Summary` | `basics.summary` | *(no entries)* | `basics.summary` | — | — |
| `Work` | `work` | `name` — `position` | `summary` | `highlights` | **yes** |
| `Volunteer` | `volunteer` | `organization` — `position` | `summary` | `highlights` | **yes** |
| `Education` | `education` | `institution` — `area` | *(rejected)* | `courses` | no |
| `Projects` | `projects` | `name` | `description` | `highlights` | **yes** |
| `Skills` | `skills` | `name` | *(rejected)* | `keywords` | no |
| `Awards` | `awards` | `title` | `summary` | *(rejected)* | — |
| `Certificates` | `certificates` | `name` | *(rejected)* | *(rejected)* | — |
| `Publications` | `publications` | `name` | *(rejected)* | *(rejected)* | — |
| `Languages` | `languages` | `language` | *(rejected)* | *(rejected)* | — |
| `Interests` | `interests` | `name` | *(rejected)* | `keywords` | no |
| `References` | `references` | `name` | `reference` | *(rejected)* | — |

"*(rejected)*" means a hard build error, not a silent drop:
`'Certificates' entries take no prose paragraph` /
`'Languages' entries take no bullet list`.

Bullets always serialise as **plain strings** in a JSON array. The `{#id}`
permission is the only difference the "highlights" sections get; the ID itself
is consumed by the provenance gate and never appears in the JSON.

## Meta keys

Every key in a `<!--meta … -->` block is copied into the entry object, except:

- `id` — a human handle for the entry. **Never emitted.**
- `start` → renamed to `startDate`
- `end` → renamed to `endDate`

Which keys each section may carry is decided by the schema gate
(`SECTION_FIELDS` in `jsonresume_schema.py`). Fields already supplied by the
heading, the prose, or the bullets are marked below; supplying them again via
meta is legal but pointless.

| JSON key | Meta keys you may set | Required by the schema |
|---|---|---|
| `work` | `start`, `end`, `url`, `location`, (`summary` — prefer prose) | `name`, `position`, `startDate` |
| `volunteer` | `start`, `end`, `url`, (`summary` — prefer prose) | `organization`, `position`, `startDate` |
| `education` | `studyType`, `start`, `end`, `score`, `url` | `institution`, `area` |
| `projects` | `start`, `end`, `url`, `roles`, `keywords`, `entity`, `type` | `name` |
| `skills` | `level` | `name` |
| `awards` | `date`, `awarder`, (`summary` — prefer prose) | `title`, `date` |
| `certificates` | `date`, `issuer`, `url` | `name`, `date` |
| `publications` | `publisher`, `releaseDate`, `url`, `summary` | `name` |
| `languages` | `fluency` | `language` |
| `interests` | *(none beyond `id`)* | `name` |
| `references` | *(none beyond `id`)* — the quote is the prose | `name` |

Publications take no prose, so a publication `summary` must go in the meta block.

## Types the schema gate checks

- `str` fields must be strings.
- `list[str]` fields (`highlights`, `courses`, `keywords`, `roles`) must be
  lists of strings.
- `date` fields (`startDate`, `endDate`, `date`, `releaseDate`) must match
  `^(\d{4}-\d{2}-\d{2})?$` — a full ISO date, or `""` for open-ended.
  `"2024"` and `"2024-08"` are rejected.
- `basics.location` must be a table; `basics.profiles` a list of tables, each
  with at least `network`.
- Any key not in the section's field list is
  `unknown field for this section`.
- `basics` requires `name` and `email`.

## Where a build error points

`cv_build.py` keeps a map from JSON path to source line, so a schema violation
is reported at the Markdown line that produced it:

```
✗ cv.md:33 work[0].startDate: must be YYYY-MM-DD or empty, got '2024'
```

The line map holds an entry per `work[0]`-style path (the `## ` heading line)
and per bullet (`work[0].highlights[2]`). A field path such as
`work[0].startDate` has no line of its own, so the builder falls back to the
owning entry — meaning meta-field errors point at the entry heading, not at the
line inside the meta block. Nothing is written to disk for a file that produced
any error.
