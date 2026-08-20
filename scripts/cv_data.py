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

# Research Interests was dropped from the CV: a standalone paragraph of interests
# is the one part of a CV nobody can check. This is not that. It is the sentence
# the homepage opens with, the keywords that page carries, and three counts that
# can each be verified from the sections below - which is what the review asked
# for when it said the CV and the site should say the same thing.
SUMMARY = (
    "I study how to design human-centered agentic AI systems that help people understand "
    "their situation, make meaningful decisions, and take purposeful action. I build the "
    "systems I study - multi-agent LLM pipelines, VR tasks in Unity, and multimodal "
    "behavioral models - and test them where the judgement carries stakes: tutoring, "
    "debate, career counseling, and early cognitive screening. "
    "<b>12 peer-reviewed papers (6 first-authored)</b>, including a first-authored "
    "validation study in <i>JMIR</i> (JCR Q1, JIF 8.2); <b>1 patent filed</b>; "
    "<b>6 funded projects</b> since 2021."
)

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
            "JCR Q1; JIF 8.2; 96th percentile, rank 8/194 in Health Care Sciences &amp; Services (2026 JCR)"
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
# HCI Korea, so the two co-authored entries were doing little for the reader, and
# the HCI Korea 2025 paper is credited on its award line instead. The tree paper
# is out on the same rule -- it is co-authored -- and the SUNGHA project that
# would have carried it is out too: the records that would back a lead-researcher
# claim are not held, and one entry that cannot be cross-examined puts the rest in
# doubt. Both keep their pages on the website, which carries the full list.
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
# Every project carries its funder and the size of the award, because that is what
# a reader is weighing and leaving it out makes the entry unreadable. The award is
# the project’s, not mine - the note under the affiliation says so once, rather
# than repeating a disclaimer six times.
RESEARCH_EXPERIENCE = [
    {
        "org": "Human-centered Artificial Intelligence (HAI) Lab, SeoulTech",
        "place": "Seoul, South Korea",
        "roles": [
            ("Graduate Researcher (Advisor: Kyoungwon Seo)", "Mar. 2023 - Present"),
            ("Undergraduate Researcher", "Mar. 2021 - Feb. 2023"),
        ],
        "note": (
            "Amounts are each project’s total award, held by my advisor as principal "
            "investigator; the role given is the one I held on the research team."
        ),
        "projects": [
            {
                "title": "Usability Evaluation of a Compound AI Tutoring System",
                "role": "Lead Graduate Researcher | Tutorus Labs | KRW 30M",
                "dates": "Mar. 2026 - Aug. 2026",
                "bullets": [
                    "Designed the evaluation framework and wrote the utterance-level ICAP coding "
                    "manual, then built the classifier that applies it",
                    "Ran the sessions with school and first-year university students, and built the "
                    "analytics dashboard linking engagement to learning outcome",
                    "Produced a coded dialogue corpus and the project’s final report; journal "
                    "manuscript in preparation",
                ],
            },
            {
                "title": "Agentic AI for Personalized Career, Admission, and Counseling Support",
                "role": "Lead Graduate Researcher | Korea Education & Research Information Service | KRW 50M",
                "dates": "Jun. 2025 - Dec. 2025",
                "bullets": [
                    "Ran the teacher focus groups, designed the multi-agent workflow, and ran two "
                    "rounds of expert validation and a Delphi study",
                    "Piloted the system with 30 teachers and 150 students; experts rated the design "
                    "direction 4.37/5 and automatic record ingestion 5.00/5",
                    "Produced KERIS Research Report RR 2025-3, an invention disclosure, and a "
                    "first-authored HCI Korea 2026 paper",
                ],
            },
            {
                "title": "AI Copilot for Teacher-Augmented, Competence-Adaptive Learning",
                "role": (
                    "Lead Graduate Researcher | Institute for Information & Communications "
                    "Technology Planning & Evaluation | KRW 1B"
                ),
                "dates": "Jul. 2023 - Dec. 2025",
                "bullets": [
                    "Designed and evaluated a multi-agent LLM debate chatbot that draws out a "
                    "student’s argument and scores critical thinking from the exchange",
                    "Its evaluator agents matched human raters at an intraclass correlation of 0.78, "
                    "agreeing within one point 97.37% of the time (CHI EA 2025, first-authored)",
                    "Co-developed a self-determination-theory career counseling chatbot",
                ],
            },
            {
                "title": "AI Agents for Improving Teachers’ Instructional Design",
                "role": "Lead Graduate Researcher | Korea Education & Research Information Service",
                "dates": "2025",
                "bullets": [
                    "Authored the final report, designed the system prompts, and drafted the interface",
                    "Produced a practitioner guide to collaborative instructional-design agents",
                ],
            },
            {
                "title": "VR-EP-EEG-MRI Digital Biomarker Basic Research Laboratory",
                "role": "Lead Graduate Researcher | Ministry of Science and ICT | KRW 1.2B",
                "dates": "Jun. 2021 - Feb. 2024",
                "bullets": [
                    "Ran the VR data collection on site at Hanyang University Guri Hospital, with "
                    "patients rather than a convenience sample",
                    "Analyzed the VEEM multimodal dataset - hand movement, gaze, evoked potentials, "
                    "EEG and MRI - including the VR-MRI-SNSB cohort of 54 participants",
                    "The dataset behind four of my papers; a filed patent was submitted as a project "
                    "deliverable",
                ],
            },
            {
                "title": "Digital Biomarkers for Early Dementia Diagnosis from VR Daily-Living Data",
                "role": "Lead Graduate Researcher | Ministry of Science and ICT | KRW 550M",
                "dates": "Mar. 2021 - Feb. 2024",
                "bullets": [
                    "Built the virtual kiosk task in Unity - the six-step daily-living scenario the "
                    "study’s VR biomarkers are derived from",
                    "Led the multimodal model, deriving hand-movement and gaze features and reading "
                    "them together with MRI-derived measures",
                    "Separated 22 healthy controls from 32 patients at 94.4% accuracy, higher than VR "
                    "or MRI alone (JMIR 2024, first-authored)",
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

# Worded to match the capabilities the site's project entries claim, so a reader
# who has seen one recognises the other.
SKILLS = [
    "<b>Research Methods</b> - experimental design, usability evaluation, focus group interviews, "
    "Delphi and expert validation, school and field pilots, clinical data collection with patients, "
    "utterance-level dialogue coding, inter-rater agreement, statistical analysis",
    "<b>Machine Learning</b> - PyTorch, scikit-learn, Hugging Face, feature engineering, multimodal fusion, transfer learning, classifier development",
    "<b>LLM Systems</b> - OpenAI and Anthropic APIs, multi-agent pipelines, RAG, prompt engineering and evaluation, LLM-as-a-judge",
    "<b>Programming and Tooling</b> - Python, C/C#, Docker, Streamlit, Git, SPSS",
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
