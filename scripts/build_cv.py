from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

import cv_data


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "cv" / "Bogyeom_Park_CV.pdf"

PAGE_W, PAGE_H = letter
MARGIN_X = 0.80 * inch
MARGIN_TOP = 0.68 * inch
MARGIN_BOTTOM = 0.52 * inch

INK = colors.black
RULE = colors.black


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="Name",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=24,
        leading=27,
        textColor=INK,
        alignment=TA_CENTER,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        name="Contact",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9.2,
        leading=10.7,
        textColor=INK,
        alignment=TA_RIGHT,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11.5,
        leading=13.5,
        textColor=INK,
        spaceBefore=11,
        spaceAfter=1,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10.4,
        leading=12.6,
        textColor=INK,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="CVBullet",
        parent=styles["Body"],
        leftIndent=17,
        firstLineIndent=-10,
        bulletIndent=4,
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="EntryTitle",
        parent=styles["Body"],
        fontName="Times-Bold",
        fontSize=10.7,
        leading=12.6,
        spaceAfter=0.5,
    )
)
styles.add(
    ParagraphStyle(
        name="Meta",
        parent=styles["Body"],
        fontName="Times-Italic",
        fontSize=10.2,
        leading=12.2,
        textColor=INK,
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["Body"],
        fontSize=10.1,
        leading=12.1,
        spaceAfter=1,
    )
)
styles.add(
    ParagraphStyle(
        name="Right",
        parent=styles["Body"],
        alignment=TA_RIGHT,
        spaceAfter=0.5,
    )
)
styles.add(
    ParagraphStyle(
        name="CVItalic",
        parent=styles["Meta"],
        spaceAfter=0.5,
    )
)
styles.add(
    ParagraphStyle(
        name="CVItalicRight",
        parent=styles["Meta"],
        alignment=TA_RIGHT,
        spaceAfter=0.5,
    )
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.setFillColor(INK)
    canvas.drawCentredString(PAGE_W / 2, 0.24 * inch, str(doc.page))
    canvas.restoreState()


def section(title):
    return [
        Paragraph(title.upper(), styles["Section"]),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=6),
    ]


def bullet(text):
    return Paragraph(text, styles["CVBullet"], bulletText="•")


def two_col(left, right, left_style="EntryTitle", right_style="Right"):
    table = Table(
        [[Paragraph(left, styles[left_style]), Paragraph(right, styles[right_style])]],
        colWidths=[4.35 * inch, 1.75 * inch],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def publication(title, authors, venue):
    return KeepTogether([
        Paragraph(title, styles["EntryTitle"]),
        Paragraph(authors.replace("Bogyeom Park", "<b>Bogyeom Park</b>").replace("Hyobin Park", "<b>Hyobin Park</b>"), styles["Small"]),
        Paragraph(venue, styles["Meta"]),
        Spacer(1, 6),
    ])


def project(title, role, dates, bullets):
    items = [Paragraph(title, styles["EntryTitle"]), two_col(role, dates, "CVItalic", "CVItalicRight")]
    items.extend(bullet(item) for item in bullets)
    items.append(Spacer(1, 6))
    return [KeepTogether(items)]


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Bogyeom Park - Academic CV",
        author="Bogyeom Park",
        subject="Academic curriculum vitae",
    )
    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        PAGE_W - (2 * MARGIN_X),
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates(PageTemplate(id="CV", frames=[frame], onPage=footer))

    c = cv_data.CONTACT
    contact = Paragraph(
        '%s<br/>'
        '<link href="mailto:%s">%s</link><br/>'
        '<link href="https://%s/">%s</link><br/>'
        '<link href="%s">Google Scholar</link> · '
        '<link href="%s">GitHub</link>'
        % (c["phone"], c["email"], c["email"], c["site"], c["site"],
           c["scholar"].replace("&", "&amp;"), c["github"]),
        styles["Contact"],
    )
    header = Table(
        [[Paragraph("", styles["Body"]), Paragraph("Bogyeom Park", styles["Name"]), contact]],
        colWidths=[1.50 * inch, 2.90 * inch, 1.70 * inch],
        hAlign="LEFT",
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story = [header, Spacer(1, 5)]

    story += section("Research Interest")
    story.append(Paragraph(cv_data.RESEARCH_INTEREST["summary"], styles["Body"]))
    story += [bullet(text) for text in cv_data.RESEARCH_INTEREST["bullets"]]

    story += section("Education")
    for index, school in enumerate(cv_data.EDUCATION):
        if index:
            story.append(Spacer(1, 6))
        story.append(two_col(school["org"], school["place"]))
        story.append(two_col(school["degree"], school["dates"], "CVItalic", "CVItalicRight"))
        story += [bullet(text) for text in school["bullets"]]

    story += section("Honors & Awards")
    story += [bullet(text) for text in cv_data.AWARDS]

    story += section("Refereed Journal Article")
    story += [publication(p["title"], p["authors"], p["venue"]) for p in cv_data.JOURNAL_ARTICLES]

    story += section("Extended Abstracts")
    story += [publication(p["title"], p["authors"], p["venue"]) for p in cv_data.EXTENDED_ABSTRACTS]

    story += section("Domestic Conference Papers & Presentations")
    story += [publication(p["title"], p["authors"], p["venue"]) for p in cv_data.DOMESTIC]

    story += section("Research Experience")
    for affiliation in cv_data.RESEARCH_EXPERIENCE:
        story.append(two_col(affiliation["org"], affiliation["place"]))
        story.append(two_col(affiliation["role"], affiliation["dates"]))
        for proj in affiliation["projects"]:
            story += project(proj["title"], proj["role"], proj["dates"], proj["bullets"])

    story += section("Teaching & Mentoring")
    for index, course in enumerate(cv_data.TEACHING):
        if index:
            story.append(Spacer(1, 6))
        story.append(two_col(course["title"], course["dates"]))
        story.append(Paragraph(course["role"], styles["Meta"]))
        story += [bullet(text) for text in course["bullets"]]

    story += section("Skills")
    story += [bullet(text) for text in cv_data.SKILLS]

    story += section("Patent")
    story.append(Paragraph(cv_data.PATENT, styles["Body"]))

    story += section("Academic Service")
    story += [bullet(text) for text in cv_data.SERVICE]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
