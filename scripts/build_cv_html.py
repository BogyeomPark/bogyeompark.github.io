"""Render cv_data into the /cv/ page, between the cv:start and cv:end markers.

The PDF (build_cv.py) and this page read the same module, so the two can never
drift. Everything outside the markers - page heading, download buttons, footer -
stays hand-edited.

Usage:
  python scripts/build_cv_html.py
  python scripts/build_cv_html.py --check    # report drift, write nothing
"""

import os
import re
import sys

import cv_data

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "cv", "index.html")
START = "<!-- cv:start -->"
END = "<!-- cv:end -->"

# The data carries intentional <b> markup, so only bare ampersands are escaped.
AMP = re.compile(r"&(?!(?:amp|lt|gt|quot|#\d+);)")


def esc(text):
    return AMP.sub("&amp;", text)


def section(title, body):
    return (
        '      <section class="content-section">\n'
        '        <div class="section-heading"><h2>%s</h2></div>\n'
        "%s"
        "      </section>\n" % (esc(title), body)
    )


def bullets(items, klass="cv-list"):
    rows = "".join("          <li>%s</li>\n" % esc(i) for i in items)
    return '        <ul class="%s">\n%s        </ul>\n' % (klass, rows)


def entry(title, when, sub=None, items=(), url=None):
    head = esc(title)
    if url:
        head = '<a href="%s">%s</a>' % (url, head)
    out = '        <div class="cv-entry">\n'
    out += '          <div class="cv-row"><h3>%s</h3>%s</div>\n' % (
        head,
        '<span class="cv-when">%s</span>' % esc(when) if when else "",
    )
    if sub:
        out += '          <p class="cv-sub">%s</p>\n' % esc(sub)
    if items:
        out += bullets(items).replace("        ", "          ")
    out += "        </div>\n"
    return out


def publications(entries):
    out = ""
    for p in entries:
        out += entry(p["title"], "", sub=p["authors"], items=[p["venue"]], url=p.get("url"))
    return out


def render():
    parts = []

    ri = cv_data.RESEARCH_INTEREST
    parts.append(section(
        "Research Interest",
        '        <p class="cv-summary">%s</p>\n' % esc(ri["summary"]) + bullets(ri["bullets"]),
    ))

    parts.append(section(cv_data.SECTION_TITLES["education"], "".join(
        entry(s["org"], s["dates"], sub=s["degree"], items=s["bullets"]) for s in cv_data.EDUCATION
    )))

    parts.append(section(cv_data.SECTION_TITLES["awards"], bullets(cv_data.AWARDS)))
    parts.append(section(cv_data.SECTION_TITLES["journal"], publications(cv_data.JOURNAL_ARTICLES)))
    parts.append(section(cv_data.SECTION_TITLES["international"], publications(cv_data.EXTENDED_ABSTRACTS)))
    parts.append(section(cv_data.SECTION_TITLES["domestic"], publications(cv_data.DOMESTIC)))

    experience = ""
    for aff in cv_data.RESEARCH_EXPERIENCE:
        experience += '        <div class="cv-affiliation">\n'
        experience += '          <div class="cv-row"><h3>%s</h3><span class="cv-when">%s</span></div>\n' % (
            esc(aff["org"]), esc(aff["dates"]))
        experience += '          <p class="cv-sub">%s</p>\n' % esc(aff["role"])
        experience += "        </div>\n"
        for proj in aff["projects"]:
            experience += entry(proj["title"], proj["dates"], sub=proj["role"], items=proj["bullets"])
    parts.append(section(cv_data.SECTION_TITLES["experience"], experience))

    parts.append(section(cv_data.SECTION_TITLES["teaching"], "".join(
        entry(c["title"], c["dates"], sub=c["role"], items=c["bullets"]) for c in cv_data.TEACHING
    )))

    parts.append(section(cv_data.SECTION_TITLES["skills"], bullets(cv_data.SKILLS)))
    parts.append(section(cv_data.SECTION_TITLES["patent"], '        <p class="cv-summary">%s</p>\n' % esc(cv_data.PATENT)))
    parts.append(section(cv_data.SECTION_TITLES["service"], bullets(cv_data.SERVICE)))

    return "".join(parts)


def main():
    check = "--check" in sys.argv[1:]
    with open(PAGE, encoding="utf-8", newline="") as fh:
        page = fh.read()

    if START not in page or END not in page:
        sys.exit("cv/index.html is missing the %s / %s markers" % (START, END))

    head, rest = page.split(START, 1)
    _, tail = rest.split(END, 1)
    newline = "\r\n" if "\r\n" in page else "\n"
    body = render().replace("\r\n", "\n").replace("\n", newline)
    rebuilt = head + START + newline + body + END + tail

    if rebuilt == page:
        print("cv/index.html up to date")
        return
    if check:
        print("cv/index.html would change")
        sys.exit(1)
    with open(PAGE, "w", encoding="utf-8", newline="") as fh:
        fh.write(rebuilt)
    print("cv/index.html rewritten (%d bytes of CV body)" % len(body))


if __name__ == "__main__":
    main()
