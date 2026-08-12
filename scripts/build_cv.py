from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "cv" / "Bogyeom_Park_CV.pdf"

PAGE_W, PAGE_H = letter
MARGIN_X = 0.62 * inch
MARGIN_TOP = 0.42 * inch
MARGIN_BOTTOM = 0.42 * inch

INK = colors.HexColor("#17242a")
TEAL = colors.HexColor("#0f4c5c")
MUTED = colors.HexColor("#5f6f75")
RULE = colors.HexColor("#b9c9cc")


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="Name",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=24,
        textColor=INK,
        alignment=TA_CENTER,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="Contact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=10.2,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=11,
        textColor=TEAL,
        spaceBefore=5,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.15,
        leading=10.35,
        textColor=INK,
        spaceAfter=2.4,
    )
)
styles.add(
    ParagraphStyle(
        name="CVBullet",
        parent=styles["Body"],
        leftIndent=10,
        firstLineIndent=-7,
        bulletIndent=0,
        spaceAfter=1.5,
    )
)
styles.add(
    ParagraphStyle(
        name="EntryTitle",
        parent=styles["Body"],
        fontName="Helvetica-Bold",
        fontSize=8.55,
        leading=10.4,
        spaceAfter=1,
    )
)
styles.add(
    ParagraphStyle(
        name="Meta",
        parent=styles["Body"],
        fontSize=7.9,
        leading=9.7,
        textColor=MUTED,
        spaceAfter=1.5,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["Body"],
        fontSize=7.65,
        leading=9.25,
    )
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.45)
    canvas.line(MARGIN_X, 0.30 * inch, PAGE_W - MARGIN_X, 0.30 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 0.17 * inch, "Bogyeom Park - Academic CV")
    canvas.drawRightString(PAGE_W - MARGIN_X, 0.17 * inch, str(doc.page))
    canvas.restoreState()


def section(title):
    return [
        Paragraph(title.upper(), styles["Section"]),
        HRFlowable(width="100%", thickness=0.55, color=RULE, spaceAfter=3),
    ]


def bullet(text):
    return Paragraph(f"- {text}", styles["CVBullet"])


def two_col(left, right):
    table = Table(
        [[Paragraph(left, styles["EntryTitle"]), Paragraph(right, styles["Meta"]) ]],
        colWidths=[4.45 * inch, 2.15 * inch],
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
    return [
        Paragraph(title, styles["EntryTitle"]),
        Paragraph(authors, styles["Small"]),
        Paragraph(venue, styles["Meta"]),
        Spacer(1, 1.5),
    ]


def project(title, role, dates, bullets):
    items = [Paragraph(title, styles["EntryTitle"]), two_col(role, dates)]
    items.extend(bullet(item) for item in bullets)
    items.append(Spacer(1, 2))
    return items


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

    story = [
        Paragraph("BOGYEOM PARK", styles["Name"]),
        Paragraph(
            'Seoul, South Korea | <link href="mailto:bogyeom@seoultech.ac.kr">bogyeom@seoultech.ac.kr</link> | +82 10-3816-8811<br/>'
            '<link href="https://bogyeompark.github.io/">bogyeompark.github.io</link> | '
            '<link href="https://scholar.google.com/citations?user=HusX3nUAAAAJ&amp;hl=en">Google Scholar</link> | '
            '<link href="https://github.com/BogyeomPark">GitHub</link>',
            styles["Contact"],
        ),
    ]

    story += section("Research Interest")
    story += [
        Paragraph(
            "I design and study AI-supported learning systems that promote deeper cognitive engagement, at the intersection of AI in Education, Human-AI Interaction, and Learning Analytics.",
            styles["Body"],
        ),
        bullet("Eliciting deeper engagement - designing AI tutors that prompt learners to explain, compare, reflect, and build on dialogue rather than receive answers passively"),
        bullet("Understanding learning processes - analyzing conversational and behavioral traces to characterize cognitive engagement and connect interaction patterns with learning outcomes"),
    ]

    story += section("Education")
    story += [
        two_col("Seoul National University of Science and Technology", "Seoul, South Korea"),
        two_col("Integrated Ph.D. in Applied Artificial Intelligence", "Mar. 2023 - Present"),
        bullet("Advisor: Kyoungwon Seo"),
        Spacer(1, 1.5),
        two_col("Seoul National University of Science and Technology", "Seoul, South Korea"),
        two_col("B.S. in Electrical and Information Engineering", "Mar. 2019 - Feb. 2023"),
        bullet("GPA: 4.14/4.5 (Major GPA: 4.5/4.5)"),
        bullet("Thesis: Online Learning Support System Based on Facial Recognition"),
    ]

    story += section("Honors & Awards")
    story += [
        bullet("AI SeoulTech Graduate Scholarship (KRW 10,000,000), Seoul Scholarship Foundation, 2025"),
        bullet("Best Student Paper Award, IEEE Seoul Section, 2024"),
        bullet("National Science and Engineering Undergraduate Scholarship (full tuition), Korea Student Aid Foundation, 2021-2022"),
        bullet("Best Capstone Design Award, Seoul National University of Science and Technology, 2022"),
    ]

    story += section("Refereed Journal Article")
    story += publication(
        "Integrating Biomarkers From Virtual Reality and Magnetic Resonance Imaging for the Early Detection of Mild Cognitive Impairment Using a Multimodal Learning Approach: Validation Study",
        "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, and Kyoungwon Seo",
        "Journal of Medical Internet Research, 26, e54538 (2024) - SCIE; JCR Top 3%; Q1",
    )

    story += section("Extended Abstracts")
    story += publication(
        "Assessing Critical Thinking Through a Multi-Agent LLM-Based Debate Chatbot",
        "Bogyeom Park and Kyoungwon Seo",
        "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems",
    )
    story += publication(
        "Exploring the Multimodal Integration of VR and MRI Biomarkers for Enhanced Early Detection of Mild Cognitive Impairment",
        "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, and Kyoungwon Seo",
        "CHI EA '24: Extended Abstracts of the 2024 CHI Conference on Human Factors in Computing Systems",
    )

    story += section("Research Experience")
    story += [
        two_col("Human-centered Artificial Intelligence (HAI) Lab, SeoulTech", "Seoul, South Korea"),
        two_col("Graduate Researcher (Advisor: Kyoungwon Seo)", "Mar. 2023 - Present"),
    ]
    story += project(
        "ICAP-Based AI Tutoring System for Probability and Statistics Learning",
        "Lead Researcher | Korea Education & Research Information Service",
        "Mar. 2026 - Aug. 2026",
        [
            "Designed and evaluated an ICAP-based AI tutor that uses staged elicitation to promote active, constructive, and interactive engagement rather than answer delivery",
            "Developed an utterance-level coding and analytics workflow linking dialogue evidence with tutor correctness, usage patterns, and learning outcomes",
            "Built an interactive research dashboard for reviewing engagement labels and comparing AI-tutored learning processes",
        ],
    )

    story.append(PageBreak())

    story += project(
        "GUI Agent Technologies for Automated UX Accessibility Evaluation",
        "Research Assistant | National Research Foundation of Korea",
        "Sep. 2025 - Present",
        [
            "Designed a GUI agent capable of performing expert-level automated evaluations of UX accessibility",
            "Planned experimental protocols for validating human-AI comparative performance in accessibility assessments",
        ],
    )
    story += project(
        "Agentic AI for Personalized Career, Academic, and Counseling Support",
        "Lead Researcher | Korean Educational Development Institute",
        "Jun. 2025 - Dec. 2025",
        ["Investigated how agentic AI could support personalized educational pathways, counseling, and decision-making"],
    )
    story += project(
        "AI Copilot Technologies for Adaptive, Teacher-Augmented Learning",
        "Research Assistant | Institute for Information & Communications Technology Planning & Evaluation",
        "Jul. 2023 - Aug. 2025",
        [
            "Built counseling chatbot and analysis models supporting AI-driven student coaching",
            "Co-developed an integrated platform enabling personalized teacher-augmented learning",
        ],
    )
    story += [
        two_col("Human-centered Artificial Intelligence (HAI) Lab, SeoulTech", "Seoul, South Korea"),
        two_col("Undergraduate Researcher (Advisor: Kyoungwon Seo)", "Jul. 2021 - Feb. 2023"),
    ]
    story += project(
        "LLMs to Support Teachers in Educational Settings",
        "Research Assistant | Lab Project",
        "Mar. 2023 - Feb. 2024",
        [
            "Fine-tuned an LLM to generate student competency-analysis reports and assessed its usefulness through expert interviews",
            "Identified opportunities and limitations of LLM support for competency assessment and report generation",
        ],
    )
    story += project(
        "Multimodal Digital Biomarkers for Early Dementia Diagnosis",
        "Research Assistant | National Research Foundation of Korea",
        "Mar. 2022 - Feb. 2024",
        [
            "Collected VR kiosk interaction data from participants with mild cognitive impairment and healthy controls in collaboration with Hanyang University Guri Hospital",
            "Developed multimodal predictive models integrating VR behavioral and MRI biomarkers for early detection of mild cognitive impairment",
        ],
    )

    story += section("Teaching")
    story += [
        two_col("Deep Learning", "Fall 2023"),
        Paragraph("Teaching Assistant, Seoul National University of Science and Technology", styles["Meta"]),
        bullet("Designed a final project using CNN-based models to predict drivers' physical and cognitive states from image data"),
        bullet("Supported lectures, advised student projects, and graded assignments and examinations"),
    ]

    story += section("Skills")
    story += [
        bullet("<b>Research Methods</b> - experimental design, usability evaluation, user research, prototyping, multimodal learning analytics, statistical analysis, qualitative coding"),
        bullet("<b>AI and Data</b> - machine learning, deep learning, feature engineering, LLM applications, AI agents"),
        bullet("<b>Programming and Analysis</b> - Python, C/C#, SPSS"),
        bullet("<b>Design</b> - HCI theory, UX design, interaction prototyping, usability testing"),
    ]

    story += section("Patent")
    story += [
        Paragraph(
            "Explainable AI-Based System for Early Diagnosis and Prognosis Prediction of Alzheimer's Disease Using VR Biomarkers, and Method Thereof (Korean Patent Application No. 10-2023-0105821, filed Aug. 2023)",
            styles["Body"],
        )
    ]

    story += section("Service")
    story += [bullet("Publicity Manager, SeoulTech Human-centered Artificial Intelligence Lab")]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
