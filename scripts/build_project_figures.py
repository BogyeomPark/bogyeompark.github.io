"""One frame per project, and each frame carries a fact.

The first version of these was decoration: a ladder of framework levels, a
three-box loop, a screenshot. They sat at 1200x520 and said what the sentence
beside them already said. Every panel here shows either a number the project
produced or the pipeline it produced it with, in one frame, one type scale and
one background, so seven of them down a page read as one system.

Nothing is invented. The ratings, the correlations, the F1 range and the cohort
sizes are all on the site already, in the entries and on the paper pages. Two
projects have published no numbers - the tutoring manuscript is in preparation
and the instructional-design study produced a report - so those two show their
method instead, which is a fact about the work rather than a claim about results.

Run after adding a project:  python scripts/build_project_figures.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, MARGIN = 1200, 520, 52
SOFT, PAPER, LINE = (245, 249, 249), (255, 255, 255), (223, 231, 233)
INK, BODY, MUTED = (23, 37, 42), (70, 87, 92), (102, 120, 125)
ACCENT, PALE, WARM = (31, 66, 117), (228, 234, 244), (181, 93, 62)

SB = r"C:\Windows\Fonts\seguisb.ttf"
UI = r"C:\Windows\Fonts\segoeui.ttf"
BD = r"C:\Windows\Fonts\segoeuib.ttf"
f_title = ImageFont.truetype(BD, 32)
f_sub = ImageFont.truetype(UI, 19)
f_lab = ImageFont.truetype(SB, 21)
f_small = ImageFont.truetype(UI, 17)
f_num = ImageFont.truetype(BD, 46)
f_huge = ImageFont.truetype(BD, 72)
f_foot = ImageFont.truetype(UI, 18)


def frame(title, subtitle):
    im = Image.new("RGB", (W, H), SOFT)
    d = ImageDraw.Draw(im)
    d.text((MARGIN, 40), title, font=f_title, fill=INK)
    d.text((MARGIN, 82), subtitle, font=f_sub, fill=MUTED)
    return im, d


def foot(d, text):
    d.text((MARGIN, H - 54), text, font=f_foot, fill=BODY)


def bars(d, rows, top, bar_x, bar_w, row_h=74):
    """rows: (label, fraction, value, highlight)"""
    for i, (label, frac, value, strong) in enumerate(rows):
        y = top + i * row_h
        d.text((MARGIN, y + 4), label, font=f_lab, fill=INK if strong else BODY)
        d.rounded_rectangle([bar_x, y, bar_x + bar_w, y + 34], radius=17, fill=(233, 239, 241))
        d.rounded_rectangle([bar_x, y, bar_x + int(bar_w * frac), y + 34], radius=17,
                            fill=ACCENT if strong else (198, 210, 222))
        d.text((bar_x + bar_w + 22, y + 2), value, font=f_lab if not strong else f_lab,
               fill=ACCENT if strong else MUTED)


def pipeline(d, steps, y, box_w=232, gap=44, height=118, accent_at=None):
    x = MARGIN
    for i, (head, note) in enumerate(steps):
        strong = accent_at is not None and i == accent_at
        d.rounded_rectangle([x, y, x + box_w, y + height], radius=13,
                            fill=PALE if strong else PAPER,
                            outline=ACCENT if strong else LINE, width=2)
        d.text((x + 18, y + 24), head, font=f_lab, fill=ACCENT if strong else INK)
        for j, line in enumerate(note):
            d.text((x + 18, y + 56 + j * 24), line, font=f_small, fill=BODY)
        if i < len(steps) - 1:
            ax = x + box_w + 10
            cy = y + height / 2
            d.line([(ax, cy), (ax + gap - 22), (cy)] if False else [(ax, cy), (ax + gap - 22, cy)],
                   fill=MUTED, width=3)
            d.polygon([(ax + gap - 14, cy), (ax + gap - 24, cy - 7), (ax + gap - 24, cy + 7)], fill=MUTED)
        x += box_w + gap


def fit_source(rel, box):
    src = Image.open(os.path.join(ROOT, "assets", rel)).convert("RGB")
    bw, bh = box
    scale = min(bw / src.width, bh / src.height)
    return src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)


# --- one builder per project ------------------------------------------------

def ai_tutoring():
    im, d = frame("How an utterance becomes a measure",
                  "Every turn is coded, and the codes are read against what the learner scored")
    pipeline(d, [("Tutor dialogue", ["Text and images,", "figures and equations"]),
                 ("ICAP code", ["Passive, active,", "constructive, interactive"]),
                 ("Engagement profile", ["Per learner,", "across the session"]),
                 ("Learning outcome", ["Scored, and read", "beside the profile"])],
             y=186, height=168, accent_at=1)
    foot(d, "The coding manual and the classifier that applies it were built for this project.")
    return im


def agentic_career():
    im, d = frame("What the experts and the schools said",
                  "Two validation rounds, then a pilot in general high schools")
    bars(d, [("Design direction", 4.37 / 5, "4.37 / 5", False),
             ("Automatic record ingestion", 1.0, "5.00 / 5", True)],
         top=162, bar_x=452, bar_w=480, row_h=84)
    d.line([(MARGIN, 340), (W - MARGIN, 340)], fill=LINE, width=2)
    for i, (num, label) in enumerate((("30", "teachers"), ("150", "students"), ("1.00", "content validity index"))):
        x = MARGIN + i * 372
        d.text((x, 372), num, font=f_num, fill=ACCENT)
        d.text((x, 428), label, font=f_small, fill=BODY)
    foot(d, "Content validity index of 1.00 on the highest-rated function.")
    return im


def ai_copilot():
    im, d = frame("Do the evaluator agents agree with people?",
                  "Debate transcripts scored by separate agents, against human raters")
    for y, num, colour, head, note in (
            (166, "0.78", ACCENT, "intraclass correlation", "agent scores against human raters"),
            (318, "97.37%", INK, "agreed within one point", "on the scoring scale the study defined")):
        d.text((MARGIN, y), num, font=f_huge, fill=colour)
        x = MARGIN + d.textlength(num, font=f_huge) + 40
        d.text((x, y + 16), head, font=f_lab, fill=INK)
        d.text((x, y + 50), note, font=f_small, fill=BODY)
    d.line([(MARGIN, 288), (W - MARGIN, 288)], fill=LINE, width=2)
    foot(d, "The point of a multi-agent design: the scorer is not the arguer.")
    return im


def instructional_design():
    im, d = frame("What the agent drafts, and what the teacher keeps",
                  "The split the study asked in-service teachers to check")
    pipeline(d, [("Teacher", ["States the intent", "for the lesson"]),
                 ("Agent", ["Drafts the plan", "and the materials"]),
                 ("Teacher", ["Revises, and", "decides"])],
             y=182, box_w=306, gap=64, height=178, accent_at=1)
    foot(d, "Administrative load moves; the judgement about the class does not.")
    return im


def tree_disease():
    im, d = frame("Pre-training on plant disease, or not",
                  "Zelkova serrata, the species over half of Korea's protected trees belong to")
    bars(d, [("ImageNet weights alone", 0.92, "92.0 \u2013 96.3%", False),
             ("Plus plant-disease pre-training", 1.0, "99.45%", True)],
         top=214, bar_x=520, bar_w=396, row_h=110)
    foot(d, "F1 on an expert-validated dataset built for the project.")
    return im


def veem_brl():
    im, d = frame("Four signals, one reading",
                  "Collected on site at Hanyang University Guri Hospital")
    art = fit_source("projects/veem-brl/source.webp", (566, 300))
    im.paste(art, (W - MARGIN - art.width, 150))
    for i, (num, label) in enumerate((("54", "VR\u2013MRI\u2013SNSB cohort"),
                                      ("4", "modalities fused"),
                                      ("1", "patent filed"))):
        y = 168 + i * 92
        d.text((MARGIN, y), num, font=f_num, fill=ACCENT)
        d.text((MARGIN + 96, y + 14), label, font=f_lab, fill=BODY)
    foot(d, "The dataset four of my papers are drawn from.")
    return im


def vr_dementia():
    im, d = frame("Ordinary tasks, performed in VR",
                  "Behaviour read together with MRI to separate two clinical groups")
    art = fit_source("projects/vr-dementia-biomarker/source.webp", (540, 292))
    im.paste(art, (W - MARGIN - art.width, 152))
    d.text((MARGIN, 168), "94.4%", font=f_huge, fill=ACCENT)
    d.text((MARGIN, 254), "classification accuracy", font=f_lab, fill=INK)
    d.text((MARGIN, 292), "higher than VR or MRI on its own", font=f_small, fill=BODY)
    d.line([(MARGIN, 344), (MARGIN + 470, 344)], fill=LINE, width=2)
    d.text((MARGIN, 366), "22 healthy controls  \u00b7  32 patients", font=f_lab, fill=BODY)
    foot(d, "The kiosk task the features come from was built in Unity for this study.")
    return im


BUILDERS = {
    "ai-tutoring-cluney": ai_tutoring,
    "agentic-career-keris": agentic_career,
    "ai-copilot-iitp": ai_copilot,
    "instructional-design-keris": instructional_design,
    "tree-disease-sungha": tree_disease,
    "veem-brl": veem_brl,
    "vr-dementia-biomarker": vr_dementia,
}


def main():
    for slug, build in BUILDERS.items():
        out_dir = os.path.join(ROOT, "assets", "projects", slug)
        os.makedirs(out_dir, exist_ok=True)
        build().save(os.path.join(out_dir, "figure.webp"), "WEBP", quality=90, method=6)
        print(f"{slug:28s} built")


if __name__ == "__main__":
    main()
