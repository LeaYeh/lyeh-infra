#!/usr/bin/env python3
"""Render a JSON Resume file into self-contained HTML.

Two modes share one visual language (two-column, teal accent, uppercase
underlined section headers, bold first highlight):

  resume : one-page "DM" — grab attention in 30 seconds, fits a single A4 page.
  cv     : comprehensive, multi-page — every highlight, project, award, etc.

Pure standard library. Reads a JSON Resume (jsonresume.org) document and
writes HTML to stdout (or --out). Turn HTML into PDF with headless Chrome:

  python3 scripts/cv_render.py docs/resume/resume-a.json --mode resume > a.html
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
      --headless=new --disable-gpu --no-pdf-header-footer \\
      --print-to-pdf=a.pdf a.html
"""

import argparse
import html
import json
import sys

# ── tuning knobs (resume mode caps; cv mode shows everything) ────────────────
# Curation belongs in the Markdown, not here. These used to be 3 and 3, which
# silently dropped bullets that the .md and the published .json still carried —
# the PDF and the Gist then described the same resume differently. They are now
# high enough not to bite; `make cv-render` fails any facet that spills onto a
# second page, so overflow is caught out loud and fixed by trimming the source.
RESUME_MAX_HIGHLIGHTS = 99     # bullets per job in resume mode
RESUME_MAX_JOBS = 5            # most-recent jobs shown in resume mode
RESUME_MAX_PROJECTS = 99       # one-line projects in resume mode
ACCENT = "#1b9e8a"            # teal accent (matches existing resume photo border)
INK = "#1f2a30"              # primary text
MUTE = "#5d6b72"             # secondary text
SIDEBAR_BG = "#f3f5f4"        # left column background


# ── helpers ──────────────────────────────────────────────────────────────────
def esc(s):
    return html.escape(str(s or ""))


_MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_date(d):
    """'2024-08-01' -> 'Aug 2024'; '' -> '' (caller maps empty end to Present)."""
    if not d:
        return ""
    parts = str(d).split("-")
    try:
        year = parts[0]
        month = int(parts[1]) if len(parts) > 1 else 0
        return f"{_MONTHS[month]} {year}".strip() if month else year
    except (ValueError, IndexError):
        return esc(d)


def date_range(start, end):
    s = fmt_date(start)
    e = fmt_date(end) if end else "Present"
    if s and e:
        return f"{s} – {e}"
    return s or e


def location_str(loc):
    if isinstance(loc, dict):
        bits = [loc.get("city"), loc.get("countryCode") or loc.get("region")]
        return ", ".join(b for b in bits if b)
    return str(loc or "")


def first_paragraph(text):
    """For resume mode: the summary's first paragraph, whole.

    This used to also cut the paragraph at 320 characters and append an ellipsis,
    which silently rewrote the author's words — the PDF said something the .md and
    the published .json did not. Length is the author's call now; cv_pagecheck.py
    fails the render if the result no longer fits on one page.
    """
    if not text:
        return ""
    return text.split("\n\n")[0].strip()


# ── section renderers ─────────────────────────────────────────────────────────
def render_skills(skills):
    if not skills:
        return ""
    rows = []
    for grp in skills:
        name = esc(grp.get("name"))
        kws = grp.get("keywords") or []
        kw = " · ".join(esc(k) for k in kws)
        rows.append(
            f'<div class="skill"><div class="skill-name">{name}</div>'
            f'<div class="skill-kw">{kw}</div></div>'
        )
    return _section("Skills", "".join(rows))


def render_education(edu):
    if not edu:
        return ""
    rows = []
    for e in edu:
        inst = esc(e.get("institution"))
        study = esc(e.get("studyType"))
        area = esc(e.get("area"))
        dr = date_range(e.get("startDate"), e.get("endDate"))
        line2 = " — ".join(x for x in [study, area] if x)
        rows.append(
            f'<div class="edu"><div class="edu-inst">{inst}</div>'
            f'<div class="edu-meta">{line2}</div>'
            f'<div class="edu-date">{dr}</div></div>'
        )
    return _section("Education", "".join(rows))


def render_languages(langs):
    if not langs:
        return ""
    rows = [
        f'<div class="lang"><span>{esc(l.get("language"))}</span>'
        f'<span class="lang-lvl">{esc(l.get("fluency"))}</span></div>'
        for l in langs
    ]
    return _section("Languages", "".join(rows))


def render_certificates(certs):
    if not certs:
        return ""
    rows = []
    for c in certs:
        name = esc(c.get("name"))
        meta = " · ".join(
            x for x in [esc(c.get("issuer")), fmt_date(c.get("date"))] if x
        )
        rows.append(
            f'<div class="cert"><div class="cert-name">{name}</div>'
            f'<div class="cert-meta">{meta}</div></div>'
        )
    return _section("Certifications", "".join(rows))


def render_awards(awards):
    if not awards:
        return ""
    rows = []
    for a in awards:
        title = esc(a.get("title"))
        meta = " · ".join(
            x for x in [esc(a.get("awarder")), fmt_date(a.get("date"))] if x
        )
        body = f'<div class="award-sum">{esc(a.get("summary"))}</div>' if a.get("summary") else ""
        rows.append(
            f'<div class="award"><div class="award-title">{title}</div>'
            f'<div class="award-meta">{meta}</div>{body}</div>'
        )
    return _section("Awards", "".join(rows))


def render_work(work, mode):
    if not work:
        return ""
    jobs = work[:RESUME_MAX_JOBS] if mode == "resume" else work
    rows = []
    for j in jobs:
        pos = esc(j.get("position"))
        name = esc(j.get("name"))
        dr = date_range(j.get("startDate"), j.get("endDate"))
        loc = esc(j.get("location"))
        meta = " · ".join(x for x in [name, loc] if x)
        hls = j.get("highlights") or []
        if mode == "resume":
            hls = hls[:RESUME_MAX_HIGHLIGHTS]
        bullets = []
        for i, h in enumerate(hls):
            cls = "hl lead" if i == 0 else "hl"
            bullets.append(f'<li class="{cls}">{esc(h)}</li>')
        summary = ""
        if mode == "cv" and j.get("summary"):
            summary = f'<div class="job-sum">{esc(j.get("summary"))}</div>'
        rows.append(
            f'<div class="job"><div class="job-head">'
            f'<div class="job-title">{pos}</div>'
            f'<div class="job-date">{dr}</div></div>'
            f'<div class="job-meta">{meta}</div>{summary}'
            f'<ul class="hls">{"".join(bullets)}</ul></div>'
        )
    return _section("Experience", "".join(rows))


def render_projects(projects, mode):
    if not projects:
        return ""
    if mode == "resume":
        items = projects[:RESUME_MAX_PROJECTS]
        rows = []
        for p in items:
            name = esc(p.get("name"))
            desc = esc(p.get("description"))
            rows.append(
                f'<div class="proj-line"><span class="proj-name">{name}</span>'
                f'<span class="proj-desc"> — {desc}</span></div>'
            )
        return _section("Selected Projects", "".join(rows))
    # cv mode: full detail
    rows = []
    for p in projects:
        name = esc(p.get("name"))
        dr = date_range(p.get("startDate"), p.get("endDate"))
        desc = f'<div class="proj-full-desc">{esc(p.get("description"))}</div>'
        hls = p.get("highlights") or []
        bullets = "".join(f"<li>{esc(h)}</li>" for h in hls)
        ul = f'<ul class="hls">{bullets}</ul>' if bullets else ""
        rows.append(
            f'<div class="job"><div class="job-head">'
            f'<div class="job-title">{name}</div>'
            f'<div class="job-date">{dr}</div></div>{desc}{ul}</div>'
        )
    return _section("Projects", "".join(rows))


def render_volunteer(vol):
    if not vol:
        return ""
    rows = []
    for v in vol:
        pos = esc(v.get("position"))
        org = esc(v.get("organization"))
        dr = date_range(v.get("startDate"), v.get("endDate"))
        summ = f'<div class="job-sum">{esc(v.get("summary"))}</div>' if v.get("summary") else ""
        hls = v.get("highlights") or []
        bullets = "".join(f"<li>{esc(h)}</li>" for h in hls)
        ul = f'<ul class="hls">{bullets}</ul>' if bullets else ""
        rows.append(
            f'<div class="job"><div class="job-head">'
            f'<div class="job-title">{pos}</div>'
            f'<div class="job-date">{dr}</div></div>'
            f'<div class="job-meta">{org}</div>{summ}{ul}</div>'
        )
    return _section("Volunteer", "".join(rows))


def render_publications(pubs):
    if not pubs:
        return ""
    rows = []
    for p in pubs:
        name = esc(p.get("name"))
        meta = " · ".join(
            x for x in [esc(p.get("publisher")), fmt_date(p.get("releaseDate"))] if x
        )
        rows.append(
            f'<div class="cert"><div class="cert-name">{name}</div>'
            f'<div class="cert-meta">{meta}</div></div>'
        )
    return _section("Publications", "".join(rows))


def _section(title, body):
    return (
        f'<section class="sec"><h2 class="sec-title">{esc(title)}</h2>{body}</section>'
    )


# ── page assembly ─────────────────────────────────────────────────────────────
def render_header(basics):
    name = esc(basics.get("name"))
    label = esc(basics.get("label"))
    img = basics.get("image")
    photo = f'<img class="photo" src="{esc(img)}" alt="">' if img else ""

    contacts = []
    if basics.get("phone"):
        contacts.append(esc(basics["phone"]))
    if basics.get("email"):
        contacts.append(esc(basics["email"]))
    loc = location_str(basics.get("location"))
    if loc:
        contacts.append(esc(loc))
    for p in basics.get("profiles") or []:
        url = p.get("url") or ""
        net = p.get("network") or ""
        if url:
            contacts.append(f'<a href="{esc(url)}">{esc(net)}</a>')
    contact_html = '<span class="dot">·</span>'.join(
        f"<span>{c}</span>" for c in contacts
    )

    return (
        f'<header class="hdr"><div class="hdr-text">'
        f'<h1 class="name">{name}</h1>'
        f'<div class="label">{label}</div>'
        f'<div class="contact">{contact_html}</div>'
        f'</div>{photo}</header>'
    )


def build_html(resume, mode):
    basics = resume.get("basics") or {}

    # left sidebar
    left = [render_skills(resume.get("skills"))]
    left.append(render_education(resume.get("education")))
    left.append(render_languages(resume.get("languages")))
    left.append(render_certificates(resume.get("certificates")))
    if mode == "cv":
        left.append(render_awards(resume.get("awards")))
    left_html = "".join(x for x in left if x)

    # right main column
    right = []
    summary = basics.get("summary")
    if summary:
        text = summary if mode == "cv" else first_paragraph(summary)
        text_html = "".join(f"<p>{esc(par)}</p>" for par in text.split("\n\n"))
        right.append(f'<section class="sec summary">{text_html}</section>')
    right.append(render_work(resume.get("work"), mode))
    right.append(render_projects(resume.get("projects"), mode))
    if mode == "cv":
        right.append(render_volunteer(resume.get("volunteer")))
        right.append(render_publications(resume.get("publications")))
    right_html = "".join(x for x in right if x)

    page_class = "page mode-resume" if mode == "resume" else "page mode-cv"
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{esc(basics.get('name'))}</title><style>{CSS}</style></head>"
        f'<body class="{page_class}">{render_header(basics)}'
        f'<div class="cols"><aside class="left">{left_html}</aside>'
        f'<main class="right">{right_html}</main></div></body></html>'
    )


# ── styles ─────────────────────────────────────────────────────────────────────
CSS = f"""
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: {INK}; font-size: 10px; line-height: 1.45; -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}
.page {{ width: 210mm; min-height: 297mm; margin: 0 auto; background: #fff; }}
a {{ color: {ACCENT}; text-decoration: none; }}

/* header */
.hdr {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 16mm 14mm 6mm 14mm; gap: 10mm;
}}
.name {{ font-size: 28px; font-weight: 800; letter-spacing: 3px; margin: 0;
  text-transform: uppercase; }}
.name {{ color: {INK}; }}
.label {{ color: {ACCENT}; font-size: 11px; font-weight: 600; letter-spacing: 2px;
  text-transform: uppercase; margin-top: 4px; }}
.contact {{ color: {MUTE}; font-size: 9.5px; margin-top: 8px; }}
.contact .dot {{ margin: 0 6px; color: #b9c3c0; }}
.photo {{ width: 26mm; height: 26mm; border-radius: 50%; object-fit: cover;
  border: 2.5px solid {ACCENT}; flex: 0 0 auto; }}

/* two columns */
.cols {{ display: flex; align-items: stretch; }}
.left {{ width: 34%; background: {SIDEBAR_BG}; padding: 6mm 8mm 10mm 14mm; }}
.right {{ width: 66%; padding: 6mm 14mm 10mm 8mm; }}

/* sections */
.sec {{ margin-bottom: 6mm; }}
.sec-title {{ font-size: 11px; font-weight: 700; letter-spacing: 2px;
  text-transform: uppercase; color: {INK}; margin: 0 0 3mm 0; padding-bottom: 1.5mm;
  border-bottom: 1.5px solid {ACCENT}; }}
.summary p {{ margin: 0 0 2mm 0; color: {INK}; font-size: 10px; }}

/* skills */
.skill {{ margin-bottom: 2.6mm; }}
.skill-name {{ font-weight: 700; font-size: 9.5px; color: {INK}; }}
.skill-kw {{ color: {MUTE}; font-size: 9px; line-height: 1.5; }}

/* education / certs / awards / pubs */
.edu, .cert, .award {{ margin-bottom: 2.8mm; }}
.edu-inst, .cert-name, .award-title {{ font-weight: 700; font-size: 9.5px; }}
.edu-meta, .cert-meta, .award-meta, .edu-date {{ color: {MUTE}; font-size: 9px; }}
.edu-date {{ font-style: italic; }}
.award-sum {{ color: {MUTE}; font-size: 9px; }}

/* languages */
.lang {{ display: flex; justify-content: space-between; font-size: 9.5px;
  margin-bottom: 1.6mm; }}
.lang-lvl {{ color: {MUTE}; }}

/* experience / projects */
.job {{ margin-bottom: 4mm; }}
.job-head {{ display: flex; justify-content: space-between; align-items: baseline;
  gap: 6mm; }}
.job-title {{ font-weight: 700; font-size: 11px; color: {INK}; }}
.job-date {{ color: {MUTE}; font-size: 9px; white-space: nowrap; font-style: italic; }}
.job-meta {{ color: {ACCENT}; font-size: 9.5px; font-weight: 600; margin-top: 0.5mm; }}
.job-sum, .proj-full-desc {{ color: {MUTE}; font-size: 9.5px; margin: 1mm 0; }}
.hls {{ margin: 1.5mm 0 0 0; padding-left: 4mm; }}
.hls li {{ margin-bottom: 1mm; font-size: 9.5px; }}
.hls li.lead {{ font-weight: 700; color: {INK}; }}
.proj-line {{ margin-bottom: 1.8mm; font-size: 9.5px; }}
.proj-name {{ font-weight: 700; }}
.proj-desc {{ color: {MUTE}; }}

/* resume mode: keep it airtight on one page */
.mode-resume {{ font-size: 9.5px; }}
.mode-resume .hdr {{ padding-top: 9mm; padding-bottom: 3mm; }}
.mode-resume .left {{ padding-top: 4mm; padding-bottom: 4mm; }}
.mode-resume .right {{ padding-top: 4mm; padding-bottom: 4mm; }}
.mode-resume .sec {{ margin-bottom: 4mm; }}
.mode-resume .sec-title {{ margin-bottom: 2mm; }}
.mode-resume .job {{ margin-bottom: 3mm; }}
.mode-resume .summary p {{ margin-bottom: 1.5mm; }}
.mode-resume .hls {{ margin-top: 1mm; }}
.mode-resume .hls li {{ margin-bottom: 0.6mm; }}
.mode-resume .skill {{ margin-bottom: 1.8mm; }}
.mode-resume .skill-kw {{ line-height: 1.4; }}
.mode-resume .edu, .mode-resume .cert, .mode-resume .award {{ margin-bottom: 1.8mm; }}
.mode-resume .lang {{ margin-bottom: 1.1mm; }}
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render JSON Resume to HTML.")
    ap.add_argument("input", help="path to a JSON Resume file")
    ap.add_argument("--mode", choices=["resume", "cv"], default="resume")
    ap.add_argument("--out", help="output HTML path (default: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        resume = json.load(f)

    out = build_html(resume, args.mode)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
