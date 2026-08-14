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
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://bogyeompark.github.io"

NAME = "Bogyeom Park"
NAME_KO = "박보겸"
FORMER_NAME = "Hyobin Park"
ROLE = "Ph.D. Student"
LAB = "Human-centered Artificial Intelligence Lab"
LAB_SHORT = "SeoulTech HAI Lab"
UNIVERSITY = "Seoul National University of Science and Technology"
EMAIL = "bogyeom@seoultech.ac.kr"
LAB_URL = "https://hai.seoultech.ac.kr/index.do"
ADVISOR_URL = "https://hai.seoultech.ac.kr/subList/20000004988"
SCHOLAR_URL = "https://scholar.google.com/citations?user=HusX3nUAAAAJ&hl=en"
GITHUB_URL = "https://github.com/BogyeomPark"
ORCID_ID = "0009-0005-3046-9621"
ORCID_URL = f"https://orcid.org/{ORCID_ID}"

PORTRAIT = "/assets/bogyeom-park-224.webp"
PORTRAIT_SIZE = (224, 288)
OG_IMAGE = "/assets/og-card.jpg"
OG_IMAGE_ALT = f"{NAME} ({NAME_KO}), {ROLE} at the {LAB_SHORT}"

# research/ and projects/ were retired: dropped from the nav in fd5d842 and
# deleted outright afterwards. Their content lives on Home and Publications.
NAV = [
    ("home", "Home", "/"),
    ("publications", "Publications", "/publications/"),
    ("news", "News", "/news/"),
    ("demos", "Demos", "/demos/"),
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
        "title": NAME,
        "og_title": f"{NAME} — agentic AI that finds your blind spots",
        "description": (
            f"{NAME} builds agentic AI that finds a person’s blind spots instead of "
            "covering them — in tutoring, debate, counseling, and cognitive screening."
        ),
        "person_schema": True,
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
        "assets": ["/assets/news.css"],
        "title": f"News | {NAME}",
        "og_title": f"Research news — {NAME}",
        "description": f"Research news and milestones from {NAME}.",
    },
    {
        "file": "demos/index.html",
        "url": "/demos/",
        "nav": "demos",
        "assets": ["/assets/demos/watch.css"],
        "title": f"Demos | {NAME}",
        "og_title": f"Systems and demos — {NAME}",
        "description": (
            f"Demos from {NAME}’s research: a playable virtual kiosk test and a narrated "
            "agentic career-counseling system."
        ),
    },
    {
        "file": "demos/kiosk/index.html",
        "url": "/demos/kiosk/",
        "nav": "demos",
        "assets": ["/assets/demos/kiosk.css", "/assets/demos/kiosk-en.js", "/assets/demos/kiosk.js"],
        "title": f"Virtual Kiosk Test | {NAME}",
        "og_title": "Ordering a meal, as a cognitive test",
        "description": (
            "The six-step virtual kiosk task from our JMIR study, in a browser. Measures your time "
            "and errors beside the study’s two groups, then writes the result up two ways."
        ),
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
        "og_title": "Assessing Critical Thinking through a Multi-Agent LLM-Based Debate Chatbot",
        "description": (
            "Assessing Critical Thinking through a Multi-Agent LLM-Based Debate Chatbot "
            f"by {NAME} and Kyoungwon Seo, CHI EA 2025."
        ),
        "citation": {
            "title": "Assessing Critical Thinking through a Multi-Agent LLM-Based Debate Chatbot",
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
        "file": "publications/advancing-mci-itc2024/index.html",
        "url": "/publications/advancing-mci-itc2024/",
        "nav": "publications",
        "og_type": "article",
        "title": f"Advancing MCI Detection | {NAME}",
        "og_title": "Advancing Mild Cognitive Impairment Detection: Integrating VR, MRI, and Neuropsychological Insights",
        "description": (
            "VR behavioral biomarkers alongside MRI and neuropsychological testing for early MCI "
            "detection, reaching 94.4% accuracy. ITC-CSCC 2024."
        ),
        "citation": {
            "title": (
                "Advancing Mild Cognitive Impairment Detection: Integrating VR, MRI, and "
                "Neuropsychological Insights for Comprehensive Diagnosis"
            ),
            "authors": [NAME, "Jinseok Park", "Hojin Choi", "Hokyoung Ryu", "Kyoungwon Seo"],
            "date": "2024",
            "conference": (
                "2024 International Technical Conference on Circuits/Systems, Computers, and "
                "Communications (ITC-CSCC)"
            ),
            "firstpage": "1",
            "lastpage": "6",
            "doi": "10.1109/ITC-CSCC62988.2024.10628151",
            "pdf": "/assets/publications/advancing-mci-itc2024/paper.pdf",
        },
    },
    {
        "file": "publications/multimodal-mci-itc2024/index.html",
        "url": "/publications/multimodal-mci-itc2024/",
        "nav": "publications",
        "og_type": "article",
        "title": f"Multimodal MCI Detection with EEG, MRI and VR | {NAME}",
        "og_title": "Multimodal Machine Learning Model for MCI Detection Using EEG, MRI and VR Data",
        "description": (
            "A multimodal model combining EEG, MRI and VR behavioral data for mild cognitive "
            "impairment detection. ITC-CSCC 2024."
        ),
        "citation": {
            "title": "Multimodal Machine Learning Model for MCI Detection Using EEG, MRI and VR Data",
            "authors": ["Mariem Kallel", NAME, "Kyoungwon Seo", "Seong-Eun Kim"],
            "date": "2024",
            "conference": (
                "2024 International Technical Conference on Circuits/Systems, Computers, and "
                "Communications (ITC-CSCC)"
            ),
            "firstpage": "1",
            "lastpage": "6",
            "doi": "10.1109/ITC-CSCC62988.2024.10628204",
        },
    },
    {
        "file": "publications/veem-iceic2024/index.html",
        "url": "/publications/veem-iceic2024/",
        "nav": "publications",
        "og_type": "article",
        "title": f"VEEM Biomarkers for Early MCI Screening | {NAME}",
        "og_title": "Early Screening of Mild Cognitive Impairment Using Multimodal VR-EP-EEG-MRI (VEEM) Biomarkers",
        "description": (
            "Eye and pupil measures combined with EEG and MRI for early screening of mild cognitive "
            "impairment. ICEIC 2024."
        ),
        "citation": {
            "title": (
                "Early Screening of Mild Cognitive Impairment Using Multimodal VR-EP-EEG-MRI (VEEM) "
                "Biomarkers via Machine Learning"
            ),
            "authors": ["Se Young Kim", NAME, "Dohyun Kim", "Hojin Choi", "Jinseok Park",
                        "Hokyoung Ryu", "Kyoungwon Seo"],
            "date": "2024",
            "conference": "2024 International Conference on Electronics, Information, and Communication (ICEIC)",
            "firstpage": "1",
            "lastpage": "4",
            "doi": "10.1109/ICEIC61013.2024.10457109",
        },
    },
    {
        "file": "publications/agentic-career-hci2026/index.html",
        "url": "/publications/agentic-career-hci2026/",
        "nav": "publications",
        "og_type": "article",
        "title": f"Agentic AI for Career Counseling | {NAME}",
        "og_title": "From Teacher Needs to Agentic AI: Designing and Validating a Personalized Career Counseling System",
        "description": (
            "An agentic AI system built from teacher-stated needs to support career and college "
            "counseling, validated by domain experts. HCI Korea 2026."
        ),
        "citation": {
            "title": (
                "From Teacher Needs to Agentic AI: Designing and Validating a Personalized Career "
                "Counseling System"
            ),
            "authors": [NAME, "Mina Yoo", "Dongkuk Lee", "Mi-ae Choi", "Seona Park", "So Young Jo",
                        "Kyoungwon Seo"],
            "date": "2026",
            "conference": "Proceedings of HCI Korea 2026",
            "pdf": "/assets/publications/agentic-career-hci2026/paper.pdf",
        },
    },
    {
        "file": "publications/self-disclosure-hci2025/index.html",
        "url": "/publications/self-disclosure-hci2025/",
        "nav": "publications",
        "og_type": "article",
        "title": f"Self-Disclosing Chatbots and Self-Reflection | {NAME}",
        "og_title": "The Impact of Self-Disclosing Chatbots for Academic Stress Assessment on Student Self-Reflection",
        "description": (
            "Whether a chatbot that discloses something of its own leads students to reflect more "
            "deeply on academic stress. Best Paper Award, HCI Korea 2025."
        ),
        "citation": {
            "title": (
                "The Impact of Self-Disclosing Chatbots for Academic Stress Assessment on Student "
                "Self-Reflection"
            ),
            "authors": ["Minyoung Park", NAME, "Kyoungwon Seo"],
            "date": "2025",
            "conference": "Proceedings of HCI Korea 2025",
            "firstpage": "560",
            "lastpage": "568",
            "pdf": "/assets/publications/self-disclosure-hci2025/paper.pdf",
        },
    },
    {
        "file": "publications/heritage-tree-hci2024/index.html",
        "url": "/publications/heritage-tree-hci2024/",
        "nav": "publications",
        "og_type": "article",
        "title": f"AI Heritage Tree Disease Diagnosis | {NAME}",
        "og_title": "Artificial Intelligence-Based Heritage Tree Disease Diagnosis Using Transfer Learning",
        "description": (
            "Transfer learning for diagnosing disease in Zelkova serrata, the species that accounts "
            "for most of Korea’s protected trees. HCI Korea 2024."
        ),
        "citation": {
            "title": (
                "Artificial Intelligence-Based Heritage Tree Disease Diagnosis Using Transfer "
                "Learning: A Case Study of Zelkova serrata"
            ),
            "authors": ["Sabin Lee", NAME, "Daejung Kim", "Kyoungwon Seo"],
            "date": "2024",
            "conference": "Proceedings of HCI Korea 2024",
            "firstpage": "212",
            "lastpage": "219",
            "pdf": "/assets/publications/heritage-tree-hci2024/paper.pdf",
        },
    },
    {
        "file": "publications/counterfactual-prefactual-hci2023/index.html",
        "url": "/publications/counterfactual-prefactual-hci2023/",
        "nav": "publications",
        "og_type": "article",
        "title": f"Counterfactual vs. Prefactual Narrative AI | {NAME}",
        "og_title": "Counterfactual vs. Prefactual: Two Narrative AIs Improve Causability for Health Data by Different Mechanisms",
        "description": (
            "Two narrative explanations of an MRI report score the same on causability but work "
            "through different mechanisms. HCI Korea 2023."
        ),
        "citation": {
            "title": (
                "Counterfactual vs. Prefactual: Two Narrative AIs Improve Causability for Health Data "
                "by Different Mechanisms"
            ),
            "authors": ["Hyobin Park", "Kyoungwon Seo"],
            "date": "2023",
            "conference": "Proceedings of HCI Korea 2023",
            "firstpage": "828",
            "lastpage": "835",
            "pdf": "/assets/publications/counterfactual-prefactual-hci2023/paper.pdf",
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
        f'"identifier":{{"@type":"PropertyValue","propertyID":"ORCID","value":"{ORCID_ID}"}},',
        '"affiliation":{"@type":"Organization",'
        f'"name":"{UNIVERSITY}","department":"{LAB}"}},',
        f'"worksFor":{{"@type":"Organization","name":"{UNIVERSITY}"}},',
        f'"url":"{SITE}/",',
        f'"image":"{SITE}{OG_IMAGE}",',
        f'"email":"mailto:{EMAIL}",',
        f'"sameAs":["{SCHOLAR_URL}","{ORCID_URL}","{GITHUB_URL}"],',
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
        '  <meta name="theme-color" content="#1b3a66">',
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
        if cite.get("doi"):
            out.append(f'  <meta name="citation_doi" content="{cite["doi"]}">')
        pdf = cite.get("pdf")
        if pdf and os.path.isfile(os.path.join(ROOT, pdf.lstrip("/"))):
            out.append(f'  <meta name="citation_pdf_url" content="{SITE}{pdf}">')

    # The two latin subsets carry the first paint on every page; preloading them
    # removes the swap flash. The -ext subsets stay lazy — they cover accented
    # latin that rarely appears at all.
    out.append('  <link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>')
    out.append('  <link rel="preload" href="/assets/fonts/newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>')
    out.append(f'  <link rel="stylesheet" href="/assets/site.css?v={css_v}">')
    # Pages with their own stylesheet or script (the demos) list them here; each is
    # versioned by content hash like the shared assets.
    for asset in page.get("assets", []):
        version = asset_version(asset)
        if asset.endswith(".css"):
            out.append(f'  <link rel="stylesheet" href="{asset}?v={version}">')
        else:
            out.append(f'  <script src="{asset}?v={version}" defer></script>')
    if page.get("script"):
        out.append(f'  <script src="/assets/site.js?v={js_v}" defer></script>')
    if page.get("person_schema"):
        out.append(f'  <script type="application/ld+json">{person_schema()}</script>')
    # GoatCounter (dashboard: bogyeompark.goatcounter.com) — free, cookieless
    # visitor counts, so no consent banner is owed. count.js skips localhost on
    # its own, keeping local runs out of the numbers. kiosk.js sends two custom
    # events (run started / finished) through the same object; see its tally().
    out.append(
        '  <script data-goatcounter="https://bogyeompark.goatcounter.com/count" '
        'async src="https://gc.zgo.at/count.js"></script>'
    )
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
        # Not an <h1>: the page's own title carries that on every page, and the
        # site name repeated as <h1> gave all 18 pages the same top heading.
        f'<div class="identity"><p class="site-name"><a href="/">{NAME}</a></p>'
        f'<span class="korean-name" lang="ko">{NAME_KO}</span>'
        # "Human-Centered Agentic AI" used to sit here, directly under the lab name,
        # where it read as an expansion of HAI — which stands for Human-centered
        # Artificial Intelligence. The research area is stated on Home instead.
        f'<p class="role">{ROLE}<br>'
        f'<a href="{LAB_URL}" target="_blank" rel="noopener noreferrer">{LAB_SHORT}</a></p>'
        f'<a class="sidebar-email" href="mailto:{EMAIL}">{EMAIL}</a>'
        '</div></div>',
        '      <nav class="side-nav" aria-label="Main navigation">' + "".join(links) + "</nav>",
        '      <div class="profile-links" aria-label="External profiles">'
        f'<a href="{esc(SCHOLAR_URL)}" target="_blank" rel="noopener noreferrer">Scholar</a>'
        f'<a href="{ORCID_URL}" target="_blank" rel="noopener noreferrer">ORCID</a>'
        f'<a href="{GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a></div>',
        "    </aside>",
    ])


HEAD_RE = re.compile(r"<head>.*?</head>", re.DOTALL)
SIDEBAR_RE = re.compile(r'<aside class="sidebar".*?</aside>', re.DOTALL)

# The home footer's "Last updated" month. Hand-maintained it goes stale the
# moment a month passes; stamped at build time it is right exactly when
# something ships, because --check flags the page in a new month and forces a
# rebuild before the commit. Months are spelled out here so the stamp cannot
# vary with the machine's locale.
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
UPDATED_RE = re.compile(r"(<span data-last-updated>)[^<]*(</span>)")


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
        today = date.today()
        stamp = f"{MONTHS[today.month - 1]} {today.year}"
        text = UPDATED_RE.sub(lambda m: m.group(1) + stamp + m.group(2), text)

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
