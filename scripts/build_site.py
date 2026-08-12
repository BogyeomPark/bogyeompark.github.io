"""Sync the shared parts of every page from a single definition.

Each page keeps its own body markup and is still directly editable by hand.
This script owns only the two regions that were previously copy-pasted:

  <head> ... </head>                       title, meta, canonical, OG, icons, CSS link
  <aside class="sidebar"> ... </aside>     portrait, identity, nav, profile links

It also writes sitemap.xml and robots.txt.

The stylesheet/script cache-busting version is derived from a hash of the file
contents, so it changes exactly when the asset changes and can never drift
between pages (the previous hand-maintained ?v= string had split in two).

Usage:
  python scripts/build_site.py            # rewrite the shared regions
  python scripts/build_site.py --check    # report drift, write nothing (exit 1 if any)
"""

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://bogyeompark.github.io"

NAME = "Bogyeom Park"
NAME_KO = "박보겸"
FORMER_NAME = "Hyobin Park"
ROLE = "Integrated Ph.D. Student"
LAB = "Human-centered Artificial Intelligence Lab"
LAB_SHORT = "SeoulTech HAI Lab"
UNIVERSITY = "Seoul National University of Science and Technology"
EMAIL = "bogyeom@seoultech.ac.kr"
LAB_URL = "https://hai.seoultech.ac.kr/index.do"
ADVISOR_URL = "https://hai.seoultech.ac.kr/subList/20000004988"
SCHOLAR_URL = "https://scholar.google.com/citations?user=HusX3nUAAAAJ&hl=en"
GITHUB_URL = "https://github.com/BogyeomPark"

PORTRAIT = "/assets/bogyeom-park-224.webp"
PORTRAIT_SIZE = (224, 288)
OG_IMAGE = "/assets/og-card.jpg"
OG_IMAGE_ALT = f"{NAME} ({NAME_KO}), {ROLE} at the {LAB_SHORT}"

# research/ and projects/ were deliberately taken out of the nav in fd5d842.
# The files still exist and Home still links to them; add entries back here if
# they are ever reinstated.
NAV = [
    ("home", "Home", "/"),
    ("publications", "Publications", "/publications/"),
    ("news", "News", "/news/"),
    ("cv", "CV", "/cv/"),
]

# --- pages -----------------------------------------------------------------
# `nav` marks which nav item is current. `sidebar` False = standalone page.
# `citation` emits Google Scholar citation_* tags (paper landing pages only).

PAGES = [
    {
        "file": "index.html",
        "url": "/",
        "nav": "home",
        "title": f"{NAME} | Agentic AI Researcher",
        "og_title": f"{NAME} — Human-Centered Agentic AI",
        "description": (
            f"{NAME} is a human-centered Agentic AI researcher studying AI agents "
            "for learning, accessibility, and decision support."
        ),
        "person_schema": True,
    },
    {
        "file": "research/index.html",
        "url": "/research/",
        "nav": "research",
        "title": f"Research | {NAME}",
        "og_title": f"Research — {NAME}",
        "description": (
            f"Research interests of {NAME}: human-centered Agentic AI, AI in Education, "
            "accessibility, and agent evaluation."
        ),
    },
    {
        "file": "projects/index.html",
        "url": "/projects/",
        "nav": "projects",
        "title": f"Projects | {NAME}",
        "og_title": f"Projects — {NAME}",
        "description": f"Selected Agentic AI research projects by {NAME}.",
    },
    {
        "file": "publications/index.html",
        "url": "/publications/",
        "nav": "publications",
        "title": f"Publications | {NAME}",
        "og_title": f"Publications — {NAME}",
        "description": (
            f"Publications by {NAME} in human-centered AI, AI in Education, "
            "and multimodal learning."
        ),
    },
    {
        "file": "news/index.html",
        "url": "/news/",
        "nav": "news",
        "title": f"News | {NAME}",
        "og_title": f"Research news — {NAME}",
        "description": f"Research news and milestones from {NAME}.",
    },
    {
        "file": "cv/index.html",
        "url": "/cv/",
        "nav": "cv",
        "title": f"CV | {NAME}",
        "og_title": f"Academic CV — {NAME}",
        "description": f"Academic CV of {NAME}.",
    },
    {
        "file": "publications/debate-chatbot/index.html",
        "url": "/publications/debate-chatbot/",
        "nav": "publications",
        "script": True,
        "og_type": "article",
        "title": f"Multi-Agent Debate Chatbot | {NAME}",
        "og_title": "Assessing Critical Thinking Through a Multi-Agent LLM-Based Debate Chatbot",
        "description": (
            "Assessing Critical Thinking through a Multi-Agent LLM-Based Debate Chatbot "
            f"by {NAME} and Kyoungwon Seo, CHI EA 2025."
        ),
        "citation": {
            "title": "Assessing Critical Thinking Through a Multi-Agent LLM-Based Debate Chatbot",
            "authors": [NAME, "Kyoungwon Seo"],
            "date": "2025/04/25",
            "conference": "Extended Abstracts of the CHI Conference on Human Factors in Computing Systems",
            "firstpage": "1",
            "lastpage": "13",
            "doi": "10.1145/3706599.3721207",
            "pdf": "/assets/publications/debate-chatbot/paper.pdf",
        },
    },
    {
        "file": "publications/self-disclosure-chatbot/index.html",
        "url": "/publications/self-disclosure-chatbot/",
        "nav": "publications",
        "script": True,
        "og_type": "article",
        "title": f"Self-Disclosing Chatbots | {NAME}",
        "og_title": (
            "How Self-Disclosing Chatbots Influence Student Engagement, Assessment "
            "Accuracy, and Self-Reflection in Academic Stress Assessment"
        ),
        "description": (
            "How self-disclosing chatbots influence engagement, assessment accuracy, "
            "and self-reflection in academic stress assessment, CHI EA 2025."
        ),
        "citation": {
            "title": (
                "How Self-Disclosing Chatbots Influence Student Engagement, Assessment "
                "Accuracy, and Self-Reflection in Academic Stress Assessment"
            ),
            "authors": ["Minyoung Park", NAME, "Kyoungwon Seo"],
            "date": "2025",
            "conference": "Extended Abstracts of the CHI Conference on Human Factors in Computing Systems",
            "firstpage": "1",
            "lastpage": "10",
            "doi": "10.1145/3706599.3719684",
            "pdf": "/assets/publications/self-disclosure-chatbot/paper.pdf",
        },
    },
    {
        "file": "publications/sdt-career-chatbot/index.html",
        "url": "/publications/sdt-career-chatbot/",
        "nav": "publications",
        "script": True,
        "og_type": "article",
        "title": f"SDT Career Counseling Chatbot | {NAME}",
        "og_title": (
            "A Self-Determination Theory-Based Career Counseling Chatbot: Motivational "
            "Interactions to Address Career Decision-Making Difficulties and Enhance Engagement"
        ),
        "description": (
            "A self-determination theory-based career counseling chatbot for career "
            "decision-making and engagement, CHI EA 2025."
        ),
        "citation": {
            "title": (
                "A Self-Determination Theory-Based Career Counseling Chatbot: Motivational "
                "Interactions to Address Career Decision-Making Difficulties and Enhance Engagement"
            ),
            "authors": ["Hyerim Han", NAME, "Kyoungwon Seo"],
            "date": "2025",
            "conference": "Extended Abstracts of the CHI Conference on Human Factors in Computing Systems",
            "firstpage": "1",
            "lastpage": "9",
            "doi": "10.1145/3706599.3720286",
            "pdf": "/assets/publications/sdt-career-chatbot/paper.pdf",
        },
    },
    {
        "file": "publications/multimodal-biomarkers-jmir/index.html",
        "url": "/publications/multimodal-biomarkers-jmir/",
        "nav": "publications",
        "script": True,
        "og_type": "article",
        "title": f"Multimodal VR and MRI Biomarkers | {NAME}",
        "og_title": (
            "Integrating Biomarkers From Virtual Reality and Magnetic Resonance Imaging "
            "for the Early Detection of Mild Cognitive Impairment Using a Multimodal Learning Approach"
        ),
        "description": (
            "Integrating VR and MRI biomarkers for early MCI detection using multimodal "
            "learning, JMIR 2024."
        ),
        "citation": {
            "title": (
                "Integrating Biomarkers From Virtual Reality and Magnetic Resonance Imaging "
                "for the Early Detection of Mild Cognitive Impairment Using a Multimodal Learning Approach"
            ),
            "authors": [
                NAME, "Yuwon Kim", "Jinseok Park", "Hojin Choi",
                "Seong-Eun Kim", "Hokyoung Ryu", "Kyoungwon Seo",
            ],
            "date": "2024/04/17",
            "journal": "Journal of Medical Internet Research",
            "volume": "26",
            "firstpage": "e54538",
            "doi": "10.2196/54538",
            "pdf": "/assets/publications/multimodal-biomarkers-jmir/paper.pdf",
        },
    },
    {
        "file": "publications/vr-mri-chi/index.html",
        "url": "/publications/vr-mri-chi/",
        "nav": "publications",
        "script": True,
        "og_type": "article",
        "title": f"VR and MRI Biomarkers at CHI EA | {NAME}",
        "og_title": (
            "Exploring the Multimodal Integration of VR and MRI Biomarkers for Enhanced "
            "Early Detection of Mild Cognitive Impairment"
        ),
        "description": (
            "Exploring the integration of VR and MRI biomarkers for early MCI detection, "
            "CHI EA 2024."
        ),
        "citation": {
            "title": (
                "Exploring the Multimodal Integration of VR and MRI Biomarkers for Enhanced "
                "Early Detection of Mild Cognitive Impairment"
            ),
            "authors": [
                NAME, "Yuwon Kim", "Jinseok Park", "Hojin Choi",
                "Seong-Eun Kim", "Hokyoung Ryu", "Kyoungwon Seo",
            ],
            "date": "2024",
            "conference": "Extended Abstracts of the CHI Conference on Human Factors in Computing Systems",
            "doi": "10.1145/3613905.3651108",
            "pdf": "/assets/publications/vr-mri-chi/paper.pdf",
        },
    },
    {
        "file": "404.html",
        "url": None,
        "nav": None,
        "sidebar": False,
        "noindex": True,
        "title": f"Page Not Found | {NAME}",
        "og_title": f"Page not found — {NAME}",
        "description": "This page could not be found.",
    },
]


def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def asset_version(rel_path):
    """Short content hash, so the cache key changes iff the asset changes."""
    path = os.path.join(ROOT, rel_path.lstrip("/"))
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


def person_schema():
    lines = [
        '{"@context":"https://schema.org","@type":"Person",',
        f'"name":"{NAME}",',
        f'"alternateName":["{NAME_KO}","{FORMER_NAME}"],',
        f'"jobTitle":"{ROLE}",',
        '"affiliation":{"@type":"Organization",'
        f'"name":"{UNIVERSITY}","department":"{LAB}"}},',
        f'"worksFor":{{"@type":"Organization","name":"{UNIVERSITY}"}},',
        f'"url":"{SITE}/",',
        f'"image":"{SITE}{OG_IMAGE}",',
        f'"email":"mailto:{EMAIL}",',
        f'"sameAs":["{SCHOLAR_URL}","{GITHUB_URL}"],',
        '"knowsAbout":["Agentic AI","Human-AI Interaction","AI in Education",'
        '"Learning Analytics","Accessibility"]}',
    ]
    return "".join(lines)


def build_head(page, css_v, js_v):
    url = f"{SITE}{page['url']}" if page.get("url") else None
    og_type = page.get("og_type", "website")
    out = [
        "<head>",
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"  <title>{esc(page['title'])}</title>",
        f'  <meta name="description" content="{esc(page["description"])}">',
        f'  <meta name="author" content="{NAME}">',
        '  <meta name="theme-color" content="#0f4c5c">',
    ]
    if page.get("noindex"):
        out.append('  <meta name="robots" content="noindex">')
    if url:
        out.append(f'  <link rel="canonical" href="{url}">')
    out += [
        '  <link rel="icon" href="/assets/favicon.ico" sizes="any">',
        '  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
        f'  <meta property="og:type" content="{og_type}">',
        f'  <meta property="og:site_name" content="{NAME}">',
        f'  <meta property="og:title" content="{esc(page["og_title"])}">',
        f'  <meta property="og:description" content="{esc(page["description"])}">',
    ]
    if url:
        out.append(f'  <meta property="og:url" content="{url}">')
    out += [
        f'  <meta property="og:image" content="{SITE}{OG_IMAGE}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        f'  <meta property="og:image:alt" content="{esc(OG_IMAGE_ALT)}">',
        '  <meta name="twitter:card" content="summary_large_image">',
    ]

    cite = page.get("citation")
    if cite:
        out.append(f'  <meta name="citation_title" content="{esc(cite["title"])}">')
        for author in cite["authors"]:
            out.append(f'  <meta name="citation_author" content="{esc(author)}">')
        out.append(f'  <meta name="citation_publication_date" content="{cite["date"]}">')
        if cite.get("journal"):
            out.append(f'  <meta name="citation_journal_title" content="{esc(cite["journal"])}">')
        if cite.get("conference"):
            out.append(f'  <meta name="citation_conference_title" content="{esc(cite["conference"])}">')
        if cite.get("volume"):
            out.append(f'  <meta name="citation_volume" content="{cite["volume"]}">')
        if cite.get("firstpage"):
            out.append(f'  <meta name="citation_firstpage" content="{cite["firstpage"]}">')
        if cite.get("lastpage"):
            out.append(f'  <meta name="citation_lastpage" content="{cite["lastpage"]}">')
        out.append(f'  <meta name="citation_doi" content="{cite["doi"]}">')
        pdf = cite.get("pdf")
        if pdf and os.path.isfile(os.path.join(ROOT, pdf.lstrip("/"))):
            out.append(f'  <meta name="citation_pdf_url" content="{SITE}{pdf}">')

    out.append(f'  <link rel="stylesheet" href="/assets/site.css?v={css_v}">')
    if page.get("script"):
        out.append(f'  <script src="/assets/site.js?v={js_v}" defer></script>')
    if page.get("person_schema"):
        out.append(f'  <script type="application/ld+json">{person_schema()}</script>')
    out.append("</head>")
    return "\n".join(out)


def build_sidebar(page):
    current = page.get("nav")
    links = []
    for key, label, href in NAV:
        mark = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{mark}>{label}</a>')
    w, h = PORTRAIT_SIZE
    return "\n".join([
        '<aside class="sidebar" aria-label="Profile and navigation">',
        '      <div class="sidebar-top">'
        f'<img class="profile-photo" src="{PORTRAIT}" width="{w}" height="{h}" '
        f'alt="Portrait of {NAME}">'
        f'<div class="identity"><h1><a href="/">{NAME}</a></h1>'
        f'<span class="korean-name" lang="ko">{NAME_KO}</span>'
        f'<p class="role">{ROLE}<br>'
        f'<a href="{LAB_URL}" target="_blank" rel="noopener noreferrer">{LAB_SHORT}</a>'
        '<br>Human-Centered Agentic AI</p></div></div>',
        '      <nav class="side-nav" aria-label="Main navigation">' + "".join(links) + "</nav>",
        '      <div class="profile-links" aria-label="External profiles">'
        f'<a href="{esc(SCHOLAR_URL)}" target="_blank" rel="noopener noreferrer">Scholar</a>'
        f'<a href="{GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a>'
        f'<a href="mailto:{EMAIL}">Email</a></div>',
        f'      <p class="sidebar-note">{LAB}<br>{UNIVERSITY}</p>',
        "    </aside>",
    ])


HEAD_RE = re.compile(r"<head>.*?</head>", re.DOTALL)
SIDEBAR_RE = re.compile(r'<aside class="sidebar".*?</aside>', re.DOTALL)


def replace_once(text, pattern, replacement, what, rel):
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit(f"{rel}: expected exactly one {what} block, found {len(found)}")
    return pattern.sub(lambda _: replacement, text, count=1)


def sitemap():
    urls = [p["url"] for p in PAGES if p.get("url")]
    body = "\n".join(f"  <url><loc>{SITE}{u}</loc></url>" for u in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n"
    )


def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


def write_if_changed(path, content, check, changed, newline="\n"):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    existing = None
    if os.path.isfile(path):
        with open(path, encoding="utf-8", newline="") as fh:
            existing = fh.read()
    normalized = content.replace("\r\n", "\n").replace("\n", newline)
    if existing == normalized:
        print(f"  = {rel}")
        return
    changed.append(rel)
    if check:
        print(f"  ~ {rel} (would change)")
        return
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(normalized)
    print(f"  * {rel}")


def main():
    check = "--check" in sys.argv[1:]
    css_v = asset_version("/assets/site.css")
    js_v = asset_version("/assets/site.js")
    print(f"asset version  css={css_v}  js={js_v}")

    changed = []
    print("pages")
    for page in PAGES:
        path = os.path.join(ROOT, page["file"].replace("/", os.sep))
        rel = page["file"]
        if not os.path.isfile(path):
            raise SystemExit(f"missing page: {rel}")
        with open(path, encoding="utf-8", newline="") as fh:
            raw = fh.read()
        newline = "\r\n" if "\r\n" in raw else "\n"
        text = raw.replace("\r\n", "\n")

        text = replace_once(text, HEAD_RE, build_head(page, css_v, js_v), "head", rel)
        if page.get("sidebar", True):
            text = replace_once(text, SIDEBAR_RE, build_sidebar(page), "sidebar", rel)

        write_if_changed(path, text, check, changed, newline)

    print("generated")
    write_if_changed(os.path.join(ROOT, "sitemap.xml"), sitemap(), check, changed)
    write_if_changed(os.path.join(ROOT, "robots.txt"), robots(), check, changed)

    if check and changed:
        print(f"\n{len(changed)} file(s) out of sync")
        sys.exit(1)
    print(f"\n{len(changed)} file(s) {'to update' if check else 'updated'}")


if __name__ == "__main__":
    main()
