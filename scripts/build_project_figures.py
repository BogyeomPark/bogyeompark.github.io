"""One frame for every project figure.

The sources are a screenshot, two paper figures, an icon grid and a photo grid:
five aspect ratios, five margins, five background colours. Side by side down a
page they read as five different sites. Each one is composited into the same
1200x520 frame on the same background with the same margin, so the page has a
rhythm instead of a collection.

Two projects have no publishable artwork - one is under a company contract, the
other produced only a report. They get a diagram of their own structure in the
same frame rather than a gap: the ICAP ladder the tutoring study measures
against, and the loop the instructional-design agent sits in. Both are drawn
from what the projects are, not from data they did not produce.

Run after adding a project:  python scripts/build_project_figures.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, MARGIN = 1200, 520, 46
SOFT, PAPER, LINE = (245, 249, 249), (255, 255, 255), (223, 231, 233)
INK, BODY, MUTED = (23, 37, 42), (70, 87, 92), (102, 120, 125)
ACCENT, ACCENT_PALE, WARM = (31, 66, 117), (228, 234, 244), (181, 93, 62)

SB = r"C:\Windows\Fonts\seguisb.ttf"
UI = r"C:\Windows\Fonts\segoeui.ttf"
BD = r"C:\Windows\Fonts\segoeuib.ttf"

# slug -> source image, relative to assets/
# slug -> (source, optional crop as fractions of the source)
SOURCES = {
    "agentic-career-keris": "demos/career-agent/thumb.webp",
    # the paper figure is four stages of dialogue side by side; at this width
    # only one of them is readable, so only one of them is shown
    "ai-copilot-iitp": ("publications/debate-chatbot/figure-1.webp", (0.0, 0.0, 0.5, 0.52)),
    "tree-disease-sungha": "publications/heritage-tree-hci2024/figure-2.webp",
    "veem-brl": "projects/veem-brl/source.webp",
    "vr-dementia-biomarker": "projects/vr-dementia-biomarker/source.webp",
}


def frame():
    im = Image.new("RGB", (W, H), SOFT)
    return im, ImageDraw.Draw(im)


def fit(slug, spec):
    """Same frame, same margin, artwork centred at whatever size it arrives."""
    rel, crop = spec if isinstance(spec, tuple) else (spec, None)
    src = Image.open(os.path.join(ROOT, "assets", rel)).convert("RGB")
    if crop:
        l, t, r, b = crop
        src = src.crop((round(l * src.width), round(t * src.height),
                        round(r * src.width), round(b * src.height)))
    box_w, box_h = W - MARGIN * 2, H - MARGIN * 2
    scale = min(box_w / src.width, box_h / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    im, _ = frame()
    im.paste(src, ((W - src.width) // 2, (H - src.height) // 2))
    return im


def icap():
    """The four levels the tutoring study codes each utterance against."""
    im, d = frame()
    d.text((MARGIN, 44), "ICAP", font=ImageFont.truetype(BD, 34), fill=INK)
    d.text((MARGIN, 88), "What the learner is doing, not what the tutor said",
           font=ImageFont.truetype(UI, 20), fill=MUTED)
    levels = [("Passive", "receives"), ("Active", "manipulates"),
              ("Constructive", "generates"), ("Interactive", "builds with the tutor")]
    f_name = ImageFont.truetype(SB, 24)
    f_note = ImageFont.truetype(UI, 18)
    x, y, w, gap = MARGIN, 168, 252, 16
    for i, (name, note) in enumerate(levels):
        h = 86 + i * 44
        top = y + (176 - h)
        colour = ACCENT if i == len(levels) - 1 else ACCENT_PALE
        d.rounded_rectangle([x, top, x + w, y + 176], radius=12, fill=colour)
        d.text((x + 20, top + 18), name, font=f_name, fill=PAPER if i == 3 else ACCENT)
        d.text((x + 20, top + 50), note, font=f_note, fill=PAPER if i == 3 else BODY)
        x += w + gap
    d.text((MARGIN, 420), "Staged elicitation moves a learner up the ladder; delivering the answer does not.",
           font=ImageFont.truetype(UI, 19), fill=BODY)
    return im


def instructional_loop():
    """Where the agent sits in a teacher's lesson-design work."""
    im, d = frame()
    d.text((MARGIN, 44), "Collaborative lesson design", font=ImageFont.truetype(BD, 34), fill=INK)
    d.text((MARGIN, 88), "The agent drafts; the teacher keeps the decisions",
           font=ImageFont.truetype(UI, 20), fill=MUTED)
    steps = [("Teacher", "states the intent"), ("Agent", "drafts the plan"),
             ("Teacher", "revises and decides")]
    f_who = ImageFont.truetype(SB, 26)
    f_note = ImageFont.truetype(UI, 19)
    x, y, w, h = MARGIN, 190, 322, 132
    for i, (who, note) in enumerate(steps):
        is_agent = who == "Agent"
        d.rounded_rectangle([x, y, x + w, y + h], radius=14,
                            fill=ACCENT_PALE if is_agent else PAPER,
                            outline=ACCENT if is_agent else LINE, width=2)
        d.text((x + 24, y + 30), who, font=f_who, fill=ACCENT if is_agent else INK)
        d.text((x + 24, y + 70), note, font=f_note, fill=BODY)
        if i < len(steps) - 1:
            ax = x + w + 12
            d.line([(ax, y + h / 2), (ax + 28, y + h / 2)], fill=MUTED, width=3)
            d.polygon([(ax + 34, y + h / 2), (ax + 24, y + h / 2 - 7), (ax + 24, y + h / 2 + 7)], fill=MUTED)
        x += w + 52
    d.text((MARGIN, 386), "The loop the practitioner guide describes, and the part the study asked teachers about.",
           font=ImageFont.truetype(UI, 19), fill=BODY)
    return im


DRAWN = {"ai-tutoring-cluney": icap, "instructional-design-keris": instructional_loop}


def main():
    for slug, spec in SOURCES.items():
        out_dir = os.path.join(ROOT, "assets", "projects", slug)
        os.makedirs(out_dir, exist_ok=True)
        fit(slug, spec).save(os.path.join(out_dir, "figure.webp"), "WEBP", quality=88, method=6)
        print(f"{slug:28s} composited")
    for slug, draw in DRAWN.items():
        out_dir = os.path.join(ROOT, "assets", "projects", slug)
        os.makedirs(out_dir, exist_ok=True)
        draw().save(os.path.join(out_dir, "figure.webp"), "WEBP", quality=88, method=6)
        print(f"{slug:28s} drawn")


if __name__ == "__main__":
    main()
