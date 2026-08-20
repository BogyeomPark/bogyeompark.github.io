"""One frame per project, and each frame shows the thing that was built.

The first version of these was decoration; the second was a data card - a bar
and three numbers - which said what the sentence beside it already said. Both
missed the point of a picture on this page, which is that you should be able to
tell what a project is by looking at it.

Five of the six now show the system itself: four are frames lifted from the
demo films in this repository, and the tutoring shot is the paper's Figure 1
with its a-e callouts painted out. The slot renders about 470px wide, so a
whole application window is illegible in it; every crop here is tight enough
that the screen reads at the size it is actually shown.

Instructional design has no system to photograph - it produced a report - so it
keeps a drawn frame, and says its method rather than claiming a result.

Nothing is invented. The ratings, the correlations and the cohort sizes on the
drawn frames are all on the site already, in the entries and on the paper pages.

Run after adding a project:  python scripts/build_project_figures.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, MARGIN = 1200, 675, 52
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
             y=214, box_w=306, gap=64, height=248, accent_at=1)
    foot(d, "Administrative load moves; the judgement about the class does not.")
    return im


def tree_disease():
    im, d = frame("Pre-training on plant disease, or not",
                  "Zelkova serrata, the species over half of Korea's protected trees belong to")
    bars(d, [("ImageNet weights alone", 0.92, "92.0 \u2013 96.3%", False),
             ("Plus plant-disease pre-training", 1.0, "99.45%", True)],
         top=262, bar_x=520, bar_w=396, row_h=148)
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


# --- home cards -------------------------------------------------------------
# The full frames are built for 1200px on the projects page. The home shows them
# in a 124px-tall box, where a 1200x520 panel lands at about a tenth of its size
# and every one of them turns into the same grey rectangle. So the cards get
# their own frame: one fact, set large enough to survive the shrink. Same
# palette and type, so the two sizes still read as one system.
TW, TH = 900, 300
f_tnum = ImageFont.truetype(BD, 116)
f_tlab = ImageFont.truetype(SB, 30)
f_tsub = ImageFont.truetype(UI, 25)


def thumb(big, label, sub, chips=None):
    im = Image.new("RGB", (TW, TH), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, TW - 1, TH - 1], outline=LINE, width=2)
    d.text((56, 62), big, font=f_tnum, fill=ACCENT)
    w = d.textlength(big, font=f_tnum)
    d.text((56, 196), label, font=f_tlab, fill=INK)
    d.text((56, 238), sub, font=f_tsub, fill=BODY)
    if chips:
        x = max(56 + w + 60, 520)
        for i, c in enumerate(chips):
            y = 62 + i * 44
            on = i == len(chips) - 1
            d.rounded_rectangle([x, y, x + 300, y + 34], radius=8,
                                fill=PALE if on else SOFT, outline=LINE, width=1)
            d.text((x + 14, y + 6), c, font=f_tsub, fill=ACCENT if on else BODY)
    return im


THUMBS = {
    "ai-tutoring-cluney": lambda: thumb(
        "4", "ICAP levels", "every tutor reply coded against them",
        ["Passive", "Active", "Constructive", "Interactive"]),
    "agentic-career-keris": lambda: thumb(
        "5.00", "out of 5", "expert rating, automatic record ingestion"),
    "vr-dementia-biomarker": lambda: thumb(
        "94.4%", "classification accuracy", "22 healthy controls  ·  32 patients"),
}


# --- real project imagery ----------------------------------------------------
# (source, seek seconds or None for a still, crop as fractions of the source)
FILMS = os.path.join(ROOT, "assets", "demos")
SOURCES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figure-sources")

# Boxes are pixels in the source, and every edge sits in empty space - between
# two cards, between two bubbles, at the border of a photograph - so nothing is
# ever sliced through. What is left over after that rarely lands on 16:9, so the
# crop is padded out to the ratio in the source's own background colour rather
# than cut down to it.
REAL = {
    # the worked solution runs to y=640 and the panel closes at 700; the blank
    # half below that is dropped, and the white padding centres what is left
    "ai-tutoring-cluney": (
        os.path.join(SOURCES, "cluney-tutor-ui.webp"), None, (0, 10, 1703, 706)),
    # the card border is at y=44 and its heading at 52, and the Subject Selection
    # card closes at 556, so this takes both sections whole with room either
    # side and lets the white padding make up the ratio. Trimming to 16:9
    # instead was what shaved the heading and cut the last table row.
    "agentic-career-keris": (
        os.path.join(FILMS, "career-agent", "system-demo.mp4"), 30.0, (24, 34, 938, 566)),
    # the debate chatbot is what this project built; the frame that was here came
    # from the self-disclosure demo, which is a different study. 415 stops above
    # the Stage 3 banner, and the white margin either side is what the padding
    # samples, so the bands it adds are invisible
    "ai-copilot-iitp": (
        os.path.join(ROOT, "assets", "publications", "debate-chatbot", "figure-1.png"),
        None, (8, 8, 842, 415)),
    # 1276 leaves the sixth step a margin instead of ending flush against it
    "veem-brl": (
        os.path.join(FILMS, "vr-biomarker", "kiosk-playthrough.mp4"), 42.8, (30, 18, 1276, 616)),
    # 455 stops above the Base station callout, which belongs to the photograph
    # on the other side of the join and was being sliced
    "vr-dementia-biomarker": (
        os.path.join(FILMS, "vr-biomarker", "kiosk-playthrough.mp4"), 3.3, (0, 0, 809, 455)),
}

# The home card is about 212x124, where no interface text can be read, so the
# thumbnail keeps the part of the picture that reads as a shape: the handwriting,
# the two career panels, the person in the headset.
THUMB_W, THUMB_H = 960, 540   # exactly 16:9, so the card crops nothing
# Cropping again for the card sliced an equation in half and cut the report's
# text off top and bottom. At 212px nothing is legible either way, so the card
# shows the whole picture and keeps its shape intact.
REAL_THUMBS = {
    "ai-tutoring-cluney": (0.0, 0.0, 1.0, 1.0),
    "agentic-career-keris": (0.0, 0.0, 1.0, 1.0),
    "vr-dementia-biomarker": (0.0, 0.0, 1.0, 1.0),
}


def _frame(path, seconds):
    if seconds is None:
        return Image.open(path).convert("RGB")
    import subprocess, tempfile
    import imageio_ffmpeg
    tmp = os.path.join(tempfile.gettempdir(), "projfig.png")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                    "-ss", "%.2f" % seconds, "-i", path, "-frames:v", "1", tmp], check=True)
    return Image.open(tmp).convert("RGB")


def _pad_to(im, ratio):
    """Grow the shorter side with the picture's own edge colour, never crop."""
    w, h = im.size
    tw, th = (w, round(w / ratio)) if w / h > ratio else (round(h * ratio), h)
    if (tw, th) == (w, h):
        return im
    edge = im.getpixel((2, 2)) if th > h else im.getpixel((2, h - 3))
    out = Image.new("RGB", (tw, th), edge)
    out.paste(im, ((tw - w) // 2, (th - h) // 2))
    return out


def _crop_fraction(im, box, ratio):
    """A box given as fractions, then padded - used for the home thumbnails."""
    w, h = im.size
    return _pad_to(im.crop((int(box[0] * w), int(box[1] * h),
                            int(box[2] * w), int(box[3] * h))), ratio)


def real_figure(slug):
    path, seconds, box = REAL[slug]
    return _pad_to(_frame(path, seconds).crop(box), W / H).resize((W, H), Image.LANCZOS)


def main():
    for slug in list(REAL) + [k for k in BUILDERS if k not in REAL]:
        out_dir = os.path.join(ROOT, "assets", "projects", slug)
        os.makedirs(out_dir, exist_ok=True)
        if slug in REAL:
            fig = real_figure(slug)
            kind = "photographed"
        else:
            fig = BUILDERS[slug]()
            kind = "drawn"
        fig.save(os.path.join(out_dir, "figure.webp"), "WEBP", quality=90, method=6)
        if slug in REAL_THUMBS:
            _crop_fraction(fig, REAL_THUMBS[slug], THUMB_W / THUMB_H).resize(
                (THUMB_W, THUMB_H), Image.LANCZOS).save(
                os.path.join(out_dir, "thumb.webp"), "WEBP", quality=92, method=6)
        elif slug in THUMBS:
            THUMBS[slug]().save(os.path.join(out_dir, "thumb.webp"), "WEBP", quality=92, method=6)
        print(f"{slug:28s} {kind}")


if __name__ == "__main__":
    main()
