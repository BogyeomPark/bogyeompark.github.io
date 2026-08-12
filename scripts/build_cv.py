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

    contact = Paragraph(
        '+82 10-3816-8811<br/>'
        '<link href="mailto:bogyeom@seoultech.ac.kr">bogyeom@seoultech.ac.kr</link><br/>'
        '<link href="https://bogyeompark.github.io/">bogyeompark.github.io</link><br/>'
        '<link href="https://scholar.google.com/citations?user=HusX3nUAAAAJ&amp;hl=en">Google Scholar</link> · '
        '<link href="https://github.com/BogyeomPark">GitHub</link>',
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
    story += [
        Paragraph(
            "I design and study <b>human-centered agentic AI systems</b> that support learning, decision-making, and accessibility, at the intersection of Human-AI Interaction, AI in Education, and Learning Analytics.",
            styles["Body"],
        ),
        bullet("<b>Agentic AI for learning and decision support</b> - designing agents that reason with people, use tools, and adapt support while preserving human goals and oversight"),
        bullet("<b>Human-centered interaction and evaluation</b> - analyzing conversational and behavioral traces to understand engagement, accessibility, and real-world outcomes"),
    ]

    story += section("Education")
    story += [
        two_col("Seoul National University of Science and Technology", "Seoul, South Korea"),
        two_col("Integrated Ph.D. in Applied Artificial Intelligence", "Mar. 2023 - Present", "CVItalic", "CVItalicRight"),
        bullet("Advisor: Kyoungwon Seo"),
        Spacer(1, 6),
        two_col("Seoul National University of Science and Technology", "Seoul, South Korea"),
        two_col("B.S. in Electrical and Information Engineering", "Mar. 2019 - Feb. 2023", "CVItalic", "CVItalicRight"),
        bullet("Thesis: Online Learning Support System Based on Facial Recognition"),
    ]

    story += section("Honors & Awards")
    story += [
        bullet("AI SeoulTech Graduate Scholarship (KRW 10,000,000), Seoul Scholarship Foundation, 2025"),
        bullet("Best Paper Award (co-author), HCI Korea 2025"),
        bullet("Best Student Paper Bronze Award, IEEE Seoul Section, 2024"),
        bullet("National Science and Engineering Undergraduate Scholarship (full tuition), Korea Student Aid Foundation, 2021-2022"),
        bullet("Best Capstone Design Award, Seoul National University of Science and Technology, 2022"),
    ]

    story += section("Refereed Journal Article")
    story.append(publication(
        "Integrating Biomarkers From Virtual Reality and Magnetic Resonance Imaging for the Early Detection of Mild Cognitive Impairment Using a Multimodal Learning Approach: Validation Study",
        "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, and Kyoungwon Seo",
        "Journal of Medical Internet Research, 26, e54538 (2024) - SCIE; JCR Top 3%; Q1",
    ))

    story += section("Extended Abstracts")
    story.append(publication(
        "Assessing Critical Thinking Through a Multi-Agent LLM-Based Debate Chatbot",
        "Bogyeom Park and Kyoungwon Seo",
        "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems",
    ))
    story.append(publication(
        "How Self-Disclosing Chatbots Influence Student Engagement, Assessment Accuracy, and Self-Reflection in Academic Stress Assessment",
        "Minyoung Park, Bogyeom Park, and Kyoungwon Seo",
        "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems",
    ))
    story.append(publication(
        "A Self-Determination Theory-Based Career Counseling Chatbot: Motivational Interactions to Address Career Decision-Making Difficulties and Enhance Engagement",
        "Hyerim Han, Bogyeom Park, and Kyoungwon Seo",
        "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems",
    ))
    story.append(publication(
        "Exploring the Multimodal Integration of VR and MRI Biomarkers for Enhanced Early Detection of Mild Cognitive Impairment",
        "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, and Kyoungwon Seo",
        "CHI EA '24: Extended Abstracts of the 2024 CHI Conference on Human Factors in Computing Systems",
    ))

    story += section("Domestic Conference Papers & Presentations")
    story.append(publication(
        "From Teacher Needs to Agentic AI: Designing and Validating a Personalized Career Counseling System",
        "Bogyeom Park and Kyoungwon Seo",
        "Proceedings of HCI Korea 2026 - Oral Presentation",
    ))
    story.append(publication(
        "The Impact of Self-Disclosing Chatbots for Academic Stress Assessment on Student Self-Reflection",
        "Minyoung Park, Bogyeom Park, and Kyoungwon Seo",
        "Proceedings of HCI Korea 2025, pp. 560-568 - Best Paper Award",
    ))
    story.append(publication(
        "Counterfactual vs. Prefactual: Two Narrative AIs Improve Causability for Health Data by Different Mechanisms",
        "Hyobin Park (now Bogyeom Park) and Kyoungwon Seo",
        "Proceedings of HCI Korea 2023, pp. 828-835",
    ))

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

    story += section("Teaching & Mentoring")
    story += [
        two_col("Deep Learning", "Fall 2023"),
        Paragraph("Teaching Assistant, Seoul National University of Science and Technology", styles["Meta"]),
        bullet("Designed a final project using CNN-based models to predict drivers' physical and cognitive states from image data"),
        bullet("Supported lectures, advised student projects, and graded assignments and examinations"),
        Spacer(1, 6),
        two_col("2026 AX Academy Big Data Boot Camp", "May 2026 - Present"),
        Paragraph("Tutor, Hyundai Motor Group", styles["Meta"]),
        bullet("Mentored participants through project-based big data sprints and supported the development of their team projects"),
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

    story += section("Academic Service")
    story += [
        bullet("Student Volunteer, AIED 2026"),
        bullet("Publicity Manager, SeoulTech Human-centered Artificial Intelligence Lab"),
    ]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
