"""The CV, as data.

Single source for both renderers: build_cv.py lays this out as the PDF, and
build_cv_html.py writes the same content into the /cv/ page. Edit here only —
editing either renderer's output will just be overwritten on the next run.

Emphasis inside strings uses <b>…</b>; both renderers understand that tag
(reportlab natively, HTML by passing it through).
"""

CONTACT = {
    "phone": "+82 10-3816-8811",
    "email": "bogyeom@seoultech.ac.kr",
    "site": "bogyeompark.github.io",
    "scholar": "https://scholar.google.com/citations?user=HusX3nUAAAAJ&hl=en",
    "github": "https://github.com/BogyeomPark",
}

RESEARCH_INTEREST = {
    "summary": (
        "I design and study <b>human-centered agentic AI systems</b> that support learning, "
        "decision-making, and accessibility, at the intersection of Human-AI Interaction, "
        "AI in Education, and Learning Analytics."
    ),
    "bullets": [
        "<b>Agentic AI for learning and decision support</b> - designing agents that reason with "
        "people, use tools, and adapt support while preserving human goals and oversight",
        "<b>Human-centered interaction and evaluation</b> - analyzing conversational and behavioral "
        "traces to understand engagement, accessibility, and real-world outcomes",
    ],
}

EDUCATION = [
    {
        "org": "Seoul National University of Science and Technology",
        "place": "Seoul, South Korea",
        "degree": "Integrated Ph.D. in Applied Artificial Intelligence",
        "dates": "Mar. 2023 - Present",
        "bullets": ["Advisor: Kyoungwon Seo"],
    },
    {
        "org": "Seoul National University of Science and Technology",
        "place": "Seoul, South Korea",
        "degree": "B.S. in Electrical and Information Engineering",
        "dates": "Mar. 2019 - Feb. 2023",
        "bullets": ["Thesis: Online Learning Support System Based on Facial Recognition"],
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
            "JCR Q1; 96th percentile; JIF 8.2 (2025 JCR)"
        ),
        "url": "/publications/multimodal-biomarkers-jmir/",
    },
]

EXTENDED_ABSTRACTS = [
    {
        "title": "Assessing Critical Thinking Through a Multi-Agent LLM-Based Debate Chatbot",
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
        "title": "The Impact of Self-Disclosing Chatbots for Academic Stress Assessment on Student Self-Reflection",
        "authors": "Minyoung Park, Bogyeom Park, and Kyoungwon Seo",
        "venue": "Proceedings of HCI Korea 2025, pp. 560-568 - Best Paper Award",
    },
    {
        "title": (
            "Artificial Intelligence-Based Heritage Tree Disease Diagnosis Using Transfer Learning: "
            "A Case Study of Zelkova serrata"
        ),
        "authors": "Sabin Lee, Bogyeom Park, Daejung Kim, and Kyoungwon Seo",
        "venue": "Proceedings of HCI Korea 2024, pp. 212-219",
    },
    {
        "title": "Counterfactual vs. Prefactual: Two Narrative AIs Improve Causability for Health Data by Different Mechanisms",
        "authors": "Hyobin Park (now Bogyeom Park) and Kyoungwon Seo",
        "venue": "Proceedings of HCI Korea 2023, pp. 828-835",
    },
]

# Each affiliation holds the projects carried out under it, in CV order.
RESEARCH_EXPERIENCE = [
    {
        "org": "Human-centered Artificial Intelligence (HAI) Lab, SeoulTech",
        "place": "Seoul, South Korea",
        "role": "Graduate Researcher (Advisor: Kyoungwon Seo)",
        "dates": "Mar. 2023 - Present",
        "projects": [
            {
                "title": "ICAP-Based AI Tutoring System for Probability and Statistics Learning",
                "role": "Lead Researcher | Korea Education & Research Information Service",
                "dates": "Mar. 2026 - Aug. 2026",
                "bullets": [
                    "Designed and evaluated an ICAP-based AI tutor that uses staged elicitation to "
                    "promote active, constructive, and interactive engagement rather than answer delivery",
                    "Developed an utterance-level coding and analytics workflow linking dialogue evidence "
                    "with tutor correctness, usage patterns, and learning outcomes",
                    "Built an interactive research dashboard for reviewing engagement labels and "
                    "comparing AI-tutored learning processes",
                ],
            },
            {
                "title": "GUI Agent Technologies for Automated UX Accessibility Evaluation",
                "role": "Research Assistant | National Research Foundation of Korea",
                "dates": "Sep. 2025 - Present",
                "bullets": [
                    "Designed a GUI agent capable of performing expert-level automated evaluations of "
                    "UX accessibility",
                    "Planned experimental protocols for validating human-AI comparative performance in "
                    "accessibility assessments",
                ],
            },
            {
                "title": "Agentic AI for Personalized Career, Academic, and Counseling Support",
                "role": "Lead Researcher | Korean Educational Development Institute",
                "dates": "Jun. 2025 - Dec. 2025",
                "bullets": [
                    "Investigated how agentic AI could support personalized educational pathways, "
                    "counseling, and decision-making",
                ],
            },
            {
                "title": "AI Copilot Technologies for Adaptive, Teacher-Augmented Learning",
                "role": (
                    "Research Assistant | Institute for Information & Communications Technology "
                    "Planning & Evaluation"
                ),
                "dates": "Jul. 2023 - Aug. 2025",
                "bullets": [
                    "Built counseling chatbot and analysis models supporting AI-driven student coaching",
                    "Co-developed an integrated platform enabling personalized teacher-augmented learning",
                ],
            },
        ],
    },
    {
        "org": "Human-centered Artificial Intelligence (HAI) Lab, SeoulTech",
        "place": "Seoul, South Korea",
        "role": "Undergraduate Researcher (Advisor: Kyoungwon Seo)",
        "dates": "Jul. 2021 - Feb. 2023",
        "projects": [
            {
                "title": "LLMs to Support Teachers in Educational Settings",
                "role": "Research Assistant | Lab Project",
                "dates": "Mar. 2023 - Feb. 2024",
                "bullets": [
                    "Fine-tuned an LLM to generate student competency-analysis reports and assessed its "
                    "usefulness through expert interviews",
                    "Identified opportunities and limitations of LLM support for competency assessment "
                    "and report generation",
                ],
            },
            {
                "title": "Multimodal Digital Biomarkers for Early Dementia Diagnosis",
                "role": "Research Assistant | National Research Foundation of Korea",
                "dates": "Mar. 2022 - Feb. 2024",
                "bullets": [
                    "Collected VR kiosk interaction data from participants with mild cognitive impairment "
                    "and healthy controls in collaboration with Hanyang University Guri Hospital",
                    "Developed multimodal predictive models integrating VR behavioral and MRI biomarkers "
                    "for early detection of mild cognitive impairment",
                ],
            },
        ],
    },
]

TEACHING = [
    {
        "title": "Deep Learning",
        "dates": "Fall 2023",
        "role": "Teaching Assistant, Seoul National University of Science and Technology",
        "bullets": [
            "Designed a final project using CNN-based models to predict drivers' physical and "
            "cognitive states from image data",
            "Supported lectures, advised student projects, and graded assignments and examinations",
        ],
    },
    {
        "title": "2026 AX Academy Big Data Boot Camp",
        "dates": "May 2026 - Present",
        "role": "Tutor, Hyundai Motor Group",
        "bullets": [
            "Mentored participants through project-based big data sprints and supported the "
            "development of their team projects",
        ],
    },
]

SKILLS = [
    "<b>Research Methods</b> - experimental design, usability evaluation, user research, prototyping, "
    "multimodal learning analytics, statistical analysis, qualitative coding",
    "<b>AI and Data</b> - machine learning, deep learning, feature engineering, LLM applications, AI agents",
    "<b>Programming and Analysis</b> - Python, C/C#, SPSS",
    "<b>Design</b> - HCI theory, UX design, interaction prototyping, usability testing",
]

PATENT = (
    "Explainable AI-Based System for Early Diagnosis and Prognosis Prediction of Alzheimer's Disease "
    "Using VR Biomarkers, and Method Thereof (Korean Patent Application No. 10-2023-0105821, "
    "filed Aug. 2023)"
)

SERVICE = [
    "Student Volunteer, AIED 2026",
    "Publicity Manager, SeoulTech Human-centered Artificial Intelligence Lab",
]
