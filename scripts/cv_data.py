"""The CV, as data.

Single source for both renderers: build_cv.py lays this out as the PDF, and
build_cv_html.py writes the same content into the /cv/ page. Edit here only —
editing either renderer's output will just be overwritten on the next run.

Emphasis inside strings uses <b>…</b>; both renderers understand that tag
(reportlab natively, HTML by passing it through).
"""

# Section headings, shared by both renderers so the PDF and the page cannot
# disagree (they already had, once: "Extended Abstracts" vs the wider list).
SECTION_TITLES = {
    "education": "Education",
    "awards": "Honors & Awards",
    "journal": "Journal Articles",
    "international": "International Conference Papers",
    "domestic": "Korean Conference Papers",
    "experience": "Research Experience",
    "teaching": "Teaching & Mentoring",
    "skills": "Skills",
    "patent": "Patent",
    "service": "Academic Service",
}

CONTACT = {
    "phone": "+82 10-3816-8811",
    "email": "bogyeom@seoultech.ac.kr",
    "site": "bogyeompark.github.io",
    "scholar": "https://scholar.google.com/citations?user=HusX3nUAAAAJ&hl=en",
    "github": "https://github.com/BogyeomPark",
}

# Research Interests was dropped from the CV. The publication list and the project
# bullets carry the same ground, and a standalone paragraph of interests is the one
# part of a CV nobody can check.

EDUCATION = [
    {
        "org": "Seoul National University of Science and Technology",
        "place": "Seoul, South Korea",
        "degree": "Ph.D. in Applied Artificial Intelligence",
        "dates": "Mar. 2023 - Present",
        "bullets": ["Advisor: Kyoungwon Seo"],
    },
    # The B.S. runs to one line. An undergraduate thesis title competes for
    # attention with the funded projects below it and loses to them on every
    # count a reader is weighing; the degree itself is the only part that has to
    # be on record.
    {
        "org": "Seoul National University of Science and Technology",
        "place": "Seoul, South Korea",
        "degree": "B.S. in Electrical and Information Engineering",
        "dates": "Mar. 2019 - Feb. 2023",
        "bullets": [],
    },
]

AWARDS = [
    "AI SeoulTech Graduate Scholarship (KRW 10,000,000), Seoul Scholarship Foundation, 2025",
    "Best Paper Award (co-author), HCI Korea 2025",
    "Best Student Paper Bronze Award, IEEE Seoul Section, 2024",
    "National Science and Engineering Undergraduate Scholarship (full tuition), "
    "Korea Student Aid Foundation, 2021-2022",
    "Best Capstone Design Award, Seoul National University of Science and Technology, 2022",
]

JOURNAL_ARTICLES = [
    {
        "title": (
            "Integrating Biomarkers From Virtual Reality and Magnetic Resonance Imaging for the "
            "Early Detection of Mild Cognitive Impairment Using a Multimodal Learning Approach: "
            "Validation Study"
        ),
        "authors": (
            "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, "
            "and Kyoungwon Seo"
        ),
        "venue": (
            "Journal of Medical Internet Research, 26, e54538 (2024) - "
            "JCR Q1; Top 3%; JIF 8.2 (2025 JCR)"
        ),
        "url": "/publications/multimodal-biomarkers-jmir/",
    },
]

EXTENDED_ABSTRACTS = [
    {
        "title": "Assessing Critical Thinking through a Multi-Agent LLM-Based Debate Chatbot",
        "authors": "Bogyeom Park and Kyoungwon Seo",
        "venue": (
            "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems - "
            "Late-Breaking Work (32.7% acceptance; 619/1,888)"
        ),
        "url": "/publications/debate-chatbot/",
    },
    {
        "title": (
            "How Self-Disclosing Chatbots Influence Student Engagement, Assessment Accuracy, "
            "and Self-Reflection in Academic Stress Assessment"
        ),
        "authors": "Minyoung Park, Bogyeom Park, and Kyoungwon Seo",
        "venue": (
            "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems - "
            "Late-Breaking Work (32.7% acceptance; 619/1,888)"
        ),
        "url": "/publications/self-disclosure-chatbot/",
    },
    {
        "title": (
            "A Self-Determination Theory-Based Career Counseling Chatbot: Motivational Interactions "
            "to Address Career Decision-Making Difficulties and Enhance Engagement"
        ),
        "authors": "Hyerim Han, Bogyeom Park, and Kyoungwon Seo",
        "venue": (
            "CHI EA '25: Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems - "
            "Late-Breaking Work (32.7% acceptance; 619/1,888)"
        ),
        "url": "/publications/sdt-career-chatbot/",
    },
    {
        "title": (
            "Exploring the Multimodal Integration of VR and MRI Biomarkers for Enhanced Early "
            "Detection of Mild Cognitive Impairment"
        ),
        "authors": (
            "Bogyeom Park, Yuwon Kim, Jinseok Park, Hojin Choi, Seong-Eun Kim, Hokyoung Ryu, "
            "and Kyoungwon Seo"
        ),
        "venue": (
            "CHI EA '24: Extended Abstracts of the 2024 CHI Conference on Human Factors in Computing Systems - "
            "Late-Breaking Work (33.9% acceptance; 391/1,154)"
        ),
        "url": "/publications/vr-mri-chi/",
    },
    {
        "title": "Multimodal Machine Learning Model for MCI Detection Using EEG, MRI and VR Data",
        "authors": "Mariem Kallel, Bogyeom Park, Kyoungwon Seo, and Seong-Eun Kim",
        "venue": "2024 International Technical Conference on Circuits/Systems, Computers, and Communications (ITC-CSCC), pp. 1-6",
        "url": "https://doi.org/10.1109/ITC-CSCC62988.2024.10628204",
    },
    {
        "title": (
            "Advancing Mild Cognitive Impairment Detection: Integrating VR, MRI, and "
            "Neuropsychological Insights for Comprehensive Diagnosis"
        ),
        "authors": "Bogyeom Park, Jinseok Park, Hojin Choi, Hokyoung Ryu, and Kyoungwon Seo",
        "venue": "2024 International Technical Conference on Circuits/Systems, Computers, and Communications (ITC-CSCC), pp. 1-6",
        "url": "https://doi.org/10.1109/ITC-CSCC62988.2024.10628151",
    },
    {
        "title": (
            "Early Screening of Mild Cognitive Impairment Using Multimodal VR-EP-EEG-MRI "
            "(VEEM) Biomarkers via Machine Learning"
        ),
        "authors": (
            "Se Young Kim, Bogyeom Park, Dohyun Kim, Hojin Choi, Jinseok Park, Hokyoung Ryu, "
            "and Kyoungwon Seo"
        ),
        "venue": "2024 International Conference on Electronics, Information, and Communication (ICEIC), pp. 1-4",
        "url": "https://doi.org/10.1109/ICEIC61013.2024.10457109",
    },
]

# First-authored domestic papers only. An overseas committee cannot calibrate
# HCI Korea, so the two co-authored entries were doing little for the reader; the
# HCI Korea 2025 paper is credited on its award line instead, and the tree paper's
# work is described under the SUNGHA project. The full list stays on the website.
DOMESTIC = [
    {
        "title": "From Teacher Needs to Agentic AI: Designing and Validating a Personalized Career Counseling System",
        "authors": (
            "Bogyeom Park, Mina Yoo, Dongkuk Lee, Mi-ae Choi, Seona Park, So Young Jo, "
            "and Kyoungwon Seo"
        ),
        "venue": "Proceedings of HCI Korea 2026 - Oral Presentation",
    },
    {
        "title": "Counterfactual vs. Prefactual: Two Narrative AIs Improve Causability for Health Data by Different Mechanisms",
        "authors": "Hyobin Park (now Bogyeom Park) and Kyoungwon Seo",
        "venue": "Proceedings of HCI Korea 2023, pp. 828-835",
    },
]

# Each affiliation holds the projects carried out under it, in CV order.
# One affiliation, not two. The lab and the advisor have been the same since 2021,
# and splitting the block by student status printed the same org and the same name
# twice while forcing every grant that crosses Feb. 2023 into one side or the other.
# The status change is two lines here; Education already dates the degrees.
# Projects run in one reverse-chronological list underneath, by start date.
RESEARCH_EXPERIENCE = [
    {
        "org": "Human-centered Artificial Intelligence (HAI) Lab, SeoulTech",
        "place": "Seoul, South Korea",
        "roles": [
            ("Graduate Researcher (Advisor: Kyoungwon Seo)", "Mar. 2023 - Present"),
            ("Undergraduate Researcher", "Mar. 2021 - Feb. 2023"),
        ],
        "projects": [
            {
                "title": "ICAP-Based AI Tutoring System for Probability and Statistics Learning",
                "role": "Research Assistant | Tutorus Labs",
                "dates": "Mar. 2026 - Aug. 2026",
                "bullets": [
                    "Led the design and evaluation of an ICAP-based AI tutor that uses staged elicitation "
                    "to promote active, constructive, and interactive engagement rather than answer delivery",
                    "Developed an utterance-level coding and analytics workflow linking dialogue evidence "
                    "with tutor correctness, usage patterns, and learning outcomes",
                    "Built an interactive research dashboard for reviewing engagement labels and "
                    "comparing AI-tutored learning processes",
                ],
            },
            {
                "title": "Agentic AI for Personalized Career, Academic, and Counseling Support",
                "role": "Research Assistant | Korea Education & Research Information Service",
                "dates": "Jun. 2025 - Dec. 2025",
                "bullets": [
                    "Led a study of how agentic AI could support personalized educational pathways, "
                    "counseling, and decision-making",
                ],
            },
            {
                "title": "AI Copilot Technologies for Adaptive, Teacher-Augmented Learning",
                "role": (
                    "Research Assistant | Institute for Information & Communications Technology "
                    "Planning & Evaluation"
                ),
                "dates": "Jul. 2023 - Dec. 2025",
                # The debate chatbot was first-authored and built here; the SDT career
                # chatbot was co-developed. The self-disclosure study is a co-authored
                # paper rather than a system built here, so it stays in Publications.
                "bullets": [
                    "Designed and evaluated a multi-agent LLM debate chatbot that draws out a "
                    "student’s argument and assesses critical thinking from the exchange",
                    "Co-developed a self-determination-theory career counseling chatbot that "
                    "addresses career decision-making difficulties through motivational dialogue",
                ],
            },
            {
                "title": (
                    "AI-Based Early Screening and Prognosis Prediction for Landscape Tree Disease"
                ),
                "role": "Research Assistant | SUNGHA Co., Ltd.",
                "dates": "Jul. 2023 - Dec. 2023",
                "bullets": [
                    "Built an expert-validated image dataset of Zelkova serrata, the species that "
                    "accounts for more than half of Korea’s legally protected trees",
                    "Compared transfer-learning models with and without plant-disease pre-training "
                    "for early screening of tree disease",
                ],
            },
            {
                "title": "VR-EP-EEG-MRI Digital Biomarker Basic Research Laboratory",
                "role": "Research Assistant | National Research Foundation of Korea",
                "dates": "Mar. 2022 - Feb. 2024",
                "bullets": [
                    "Ran the VR data collection on site at Hanyang University Guri Hospital with patients "
                    "with mild cognitive impairment and healthy controls",
                    "Analyzed the resulting VEEM multimodal dataset - VR interaction, eye tracking, evoked "
                    "potentials, EEG and MRI - including the VR-MRI-SNSB cohort of 54 participants",
                ],
            },
            {
                "title": (
                    "Multimodal Deep Learning for Early Dementia Diagnosis from VR "
                    "Daily-Living Data"
                ),
                "role": "Research Assistant | National Research Foundation of Korea",
                "dates": "Mar. 2021 - Feb. 2024",
                # First-authored the JMIR validation study this grant produced.
                "bullets": [
                    "Developed the virtual kiosk task in Unity - the six-step daily-living scenario the "
                    "study's VR biomarkers are derived from",
                    "Led the development and validation of a multimodal model combining VR behavioral "
                    "biomarkers with MRI for early detection of mild cognitive impairment",
                    "Derived hand-movement and gaze features from the kiosk task and tested them "
                    "against MRI-derived measures in a clinical sample",
                ],
            },
        ],
    },
]

# Reverse chronological, like every other dated section here.
TEACHING = [
    {
        "title": "2026 AX Academy Big Data Boot Camp",
        "dates": "May 2026 - Aug 2026",
        "role": "Tutor, Hyundai Motor Group",
        "bullets": [
            "Mentored nine participants from across the company, each developing an individual "
            "big data project from proposal to final deliverable",
            "Advised on analysis design and revised project plans with participants through the "
            "boot camp’s project-based sprints",
        ],
    },
    {
        "title": "Deep Learning",
        "dates": "Fall 2023",
        "role": "Teaching Assistant, Seoul National University of Science and Technology",
        "bullets": [
            "Designed a final project using CNN-based models to predict drivers’ physical and "
            "cognitive states from image data",
            "Supported lectures, advised student projects, and graded assignments and examinations",
        ],
    },
]

SKILLS = [
    "<b>Research Methods</b> - experimental design, usability evaluation, user research, prototyping, "
    "multimodal learning analytics, statistical analysis, qualitative coding",
    "<b>AI and Data</b> - machine learning, deep learning, feature engineering, LLM applications, AI agents",
    "<b>Programming and Analysis</b> - Python, C/C#, SPSS",
    "<b>VR and Interactive Systems</b> - Unity, VR task development, interaction logging and eye tracking",
    "<b>Design</b> - HCI theory, UX design, interaction prototyping, usability testing",
]

PATENT = (
    "Explainable AI-Based System for Early Diagnosis and Prognosis Prediction of Alzheimer’s Disease "
    "Using VR Biomarkers, and Method Thereof (Korean Patent Application No. 10-2023-0105821, "
    "filed Aug. 2023)"
)

SERVICE = [
    "Student Volunteer, AIED 2026",
    "Publicity Manager, SeoulTech Human-centered Artificial Intelligence Lab",
]
