"""Put the CV pages on the /cv/ page, between the cv:start and cv:end markers.

The page shows the PDF itself, rendered to images by build_assets.py. A PDF in
an <iframe> is blank on much of mobile Safari — which is where a CV actually
gets opened — and restating the whole CV as HTML underneath the download button
just says the same thing twice.

What the images cost: no text selection, and screen readers cannot read them.
The PDF button covers both, and it is the version of record anyway.

Run order matters: cv_data.py -> build_cv.py (PDF) -> build_assets.py (page
images) -> this script.

Usage:
  python scripts/build_cv_html.py
  python scripts/build_cv_html.py --check    # report drift, write nothing
"""

import os
import re
import sys

from PIL import Image

import cv_data

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "cv", "index.html")
PAGES_DIR = os.path.join(ROOT, "assets", "cv", "pages")
START = "<!-- cv:start -->"
END = "<!-- cv:end -->"

# cv_data carries intentional <b> markup, so only bare ampersands are escaped.
AMP = re.compile(r"&(?!(?:amp|lt|gt|quot|#\d+);)")


def esc(text):
    return AMP.sub("&amp;", text)


def page_files():
    if not os.path.isdir(PAGES_DIR):
        sys.exit("missing %s — run scripts/build_assets.py first" % PAGES_DIR)
    files = [f for f in os.listdir(PAGES_DIR) if re.fullmatch(r"page-\d+\.webp", f)]
    if not files:
        sys.exit("no rendered CV pages in %s" % PAGES_DIR)
    return sorted(files, key=lambda f: int(re.search(r"\d+", f).group()))


def page_sections():
    """Which CV sections land on each page, so alt text says what is on it.

    "page 2 of 3" tells a screen reader nothing about the content. The section
    names are read off the PDF itself rather than guessed from cv_data order,
    because where a page breaks depends on the layout, not on the data.
    """
    try:
        import fitz  # PyMuPDF, same dependency build_assets.py rasterises with
    except ImportError:
        return []
    pdf = os.path.join(ROOT, "assets", "cv", "Bogyeom_Park_CV.pdf")
    if not os.path.isfile(pdf):
        return []
    titles = list(cv_data.SECTION_TITLES.values())
    # Whole-line match, not substring: "AI in Education" and "educational"
    # both contain "EDUCATION", which put Education on all three pages.
    found = []
    with fitz.open(pdf) as doc:
        for page in doc:
            lines = {line.strip().upper() for line in page.get_text().splitlines()}
            found.append([t for t in titles if t.upper() in lines])
    return found


def render():
    files = page_files()
    total = len(files)
    sections = page_sections()
    rows = []
    for index, name in enumerate(files, 1):
        with Image.open(os.path.join(PAGES_DIR, name)) as im:
            width, height = im.size
        alt = "Academic CV, page %d of %d" % (index, total)
        on_page = sections[index - 1] if index <= len(sections) else []
        if on_page:
            alt += ": " + ", ".join(on_page)
        rows.append(
            '        <img class="cv-page" src="/assets/cv/pages/%s" width="%d" height="%d"'
            ' decoding="async"%s alt="%s">\n'
            % (name, width, height, "" if index == 1 else ' loading="lazy"', esc(alt))
        )
    return (
        '      <section class="cv-viewer" aria-label="Academic CV, %d pages">\n'
        "%s"
        "      </section>\n" % (total, "".join(rows))
    )


def check_publications_page():
    """The publications page is hand-written but must use the CV's section names.

    They drifted once already - the page merged journal and conference work under
    one heading while the CV split them - so the same body of work read as two
    different lists depending on where a visitor landed.
    """
    path = os.path.join(ROOT, "publications", "index.html")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        page = fh.read()
    wanted = [cv_data.SECTION_TITLES[k] for k in ("journal", "international", "domestic")]
    return [t for t in wanted if t not in page and esc(t) not in page]


def main():
    check = "--check" in sys.argv[1:]

    missing = check_publications_page()
    if missing:
        print("publications/index.html is missing these CV section titles:")
        for title in missing:
            print("  -", title)
        if check:
            sys.exit(1)

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
    print("cv/index.html rewritten (%d page images)" % len(page_files()))


if __name__ == "__main__":
    main()
