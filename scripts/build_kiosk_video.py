"""Assemble the VR biomarker video: the kit, the task, the measures, the finding.

Two exports of the same 2024 CHI LBW session are used, each for what only it has.

The ordering run comes from the subtitle-free export: 3840x2160, nothing burned
into the picture, so the instruction bubbles here are drawn rather than patched
over Korean ones, and can be sized to what they actually say. Its shots are cut
so each begins exactly where the last ended, which makes the joins invisible --
the camera never moves, so skipping even a second teleports the participant's
arm and the run reads as choppy.

The equipment shot, the two step figures and the classification come from the
broadcast master, which is the only copy that has them. That one is 1920x1080
with Korean burned in: subtitles below y=900, and lettering inside the figures
themselves. The subtitles are cropped away; the lettering is covered and redrawn
in English in place, because the figures underneath are somebody's data and
redrawing them from scratch would be inventing it. The master also has its own
accuracy chart, but it reports a different analysis from the paper's, so the
results and the conclusion are built here from Table 5 instead.

Neither source is in the repo. Drop copies at tmp/kiosk-master.mp4 and
tmp/kiosk-raw.mp4, or leave them where the lab keeps them.
"""

import asyncio
import glob
import os
import re
import subprocess

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC_CANDIDATES = [
    os.path.join(ROOT, "tmp/kiosk-master.mp4"),
    os.path.expanduser(
        "~/OneDrive/바탕 화면/HAI LAB/학회/(2024) CHI/CHI LBW Video/"
        "치매 조기선별을 위한 VR 디지털 바이오마커 기술 최종.mp4"
    ),
]

RAW_CANDIDATES = [
    os.path.join(ROOT, "tmp/kiosk-raw.mp4"),
    os.path.expanduser(
        "~/OneDrive/바탕 화면/HAI LAB/학회/(2024) CHI/CHI LBW Video/자막 없는 시연 영상.mp4"
    ),
]

W, H, BAR_H = 1280, 720, 100
VID_H = H - BAR_H                # 620: the picture above the caption bar
BAR_BG = (17, 27, 36)
VOICE, RATE = "en-US-AriaNeural", "-15%"
LEAD = 0.3                       # narration starts this far into its caption
XFADE = 0.35                     # tail each shot carries for its dissolve

# The master is 1920x1080 with a burned-in Korean subtitle band from y=912.
# Cropping to 900 drops it, and the result is wider than 1280x620, so the scale
# fills the frame and the sides are trimmed instead of padded.
SRC_W, SRC_H, CROP_H = 1920, 1080, 900

SB = r"C:\Windows\Fonts\seguisb.ttf"
BD = r"C:\Windows\Fonts\segoeuib.ttf"
f_cap = ImageFont.truetype(BD, 27)
f_pill = ImageFont.truetype(BD, 30)
f_bub = ImageFont.truetype(SB, 27)
f_title = ImageFont.truetype(BD, 46)
f_step = ImageFont.truetype(SB, 34)
f_row = ImageFont.truetype(BD, 27)     # the figure gutter stops at x=300

# Sampled out of the figures themselves rather than guessed, so the English
# labels are the same colours as the series they name.
GREEN, OLIVE, NAVY = (115, 154, 91), (187, 160, 56), (16, 29, 86)
BUBBLE = (226, 198, 85)          # the master's instruction bubbles
BUBBLE_TX = (32, 30, 20)

# Site tokens, for the two charts built here rather than cut from the master.
INK, BODY, MUTED = (23, 37, 42), (70, 87, 92), (102, 120, 125)
PAPER_BG, SOFT, LINE = (255, 255, 255), (245, 249, 249), (223, 231, 233)
# VR and MRI are two identities, so their hues are checked, not chosen by eye:
# validate_palette.js passes #3f6fb5 / #b55d3e on all six checks in light mode.
# VR+MRI is not a third identity -- it is the pair combined -- so it takes a
# darker step of the VR hue as emphasis, and every bar is directly labelled.
VR_H, MRI_H, BOTH_H = (63, 111, 181), (181, 93, 62), (31, 66, 117)
TRACK = (238, 242, 246)
# Filled in from the narration's own word timings before the chart renders.
BAR_CUES = [0.3, 1.4, 2.8]

# Table 5 of the JMIR paper (2024;26:e54538), SVM on 54 participants.
# label, accuracy, specificity, sensitivity, F1, colour
RESULTS = [
    ("VR biomarkers", 88.9, 90.0, 87.5, 87.5, VR_H),
    ("MRI biomarkers", 83.3, 71.4, 90.9, 87.0, MRI_H),
    ("VR + MRI", 94.4, 90.9, 100.0, 93.3, BOTH_H),
]
COHORT = "54 participants  ·  22 healthy controls  ·  32 with mild cognitive impairment"

OUT = os.path.join(ROOT, "assets/demos/vr-biomarker/kiosk-playthrough.mp4")
POSTER = os.path.join(ROOT, "assets/demos/vr-biomarker/kiosk-poster.webp")
WORK = os.path.join(ROOT, "tmp/kiosk_build")

# (ss, dur, bubble, overlay, caption, hold) -- caption None continues the one
# before, so a single line of narration can run across several cuts. hold is a
# frozen tail in seconds, for a shot the master does not leave on screen long
# enough; it only reads as a hold if nothing in the shot was moving anyway.
#
# When each instruction is on screen, in the subtitle-free demo's own time. The
# ordering shots below are cut so that each begins exactly where the last ended,
# so the joins land on identical frames and cannot be seen; skipping a second or
# two between shots is what made an earlier cut look choppy, since the camera
# never moves and every skip teleported the participant's arm.
BUBBLES = [
    (0.00, 6.70, "Press the start\nbutton to begin"),
    (6.70, 9.40, "Eat in the store,\nnot takeout"),
    (9.40, 15.00, "For the burger,\nthe shrimp burger"),
    (15.00, 19.80, "For the side,\ncheese sticks"),
    (19.80, 24.80, "For the drink,\nCoca-Cola"),
    (24.80, 35.50, "Pay by card"),
    (35.50, 50.00, "PIN 6289,\nthen confirm"),
    (50.00, 58.00, "Then confirm"),
]
SEG = [
    (151.05, 5.40, None, None,
     "A commercial VR headset, one hand controller, two base stations.", 0),
    (3.00, 6.40, None, "raw",
     "A patient orders a hamburger set in virtual reality, told once.", 0),
    (9.40, 5.60, None, "raw",
     "Every choice has to be held in memory.", 0),
    (15.00, 4.80, None, "raw",
     "Nothing is written down, and nothing is repeated.", 0),
    (19.80, 5.00, None, "raw",
     "And the screen changes at every step.", 0),
    (24.80, 5.40, None, "raw",
     "Then the payment method, and a four-digit PIN.", 0),
    # ends on the kiosk's own "well done" screen, so the run finishes rather
    # than just stopping
    (52.40, 4.60, None, "raw",
     "Six steps, and the order is done.", 0),
    (198.30, 5.80, None, "fig:Hand movement",
     "The impaired group's hand went back and forth before it found the button.", 1.0),
    (205.10, 5.10, None, "fig:Eye movement",
     "Their gaze wandered the screen instead of settling on the answer.", 0),
    (None, 4.40, None, "gen:three",
     "So it took them longer, and more of it went wrong.", 0),
    (None, 5.40, None, "gen:model",
     "All three signals go into one model, which sorts the two groups.", 0),
    # The master's own accuracy chart is a different analysis from the paper's,
    # so from here the beats are built from Table 5 instead of cut.
    (None, 7.20, None, "gen:results",
     "VR alone beat MRI alone. Together, they beat both.", 0),
    (None, 4.20, None, "gen:conclusion",
     "VR is the specific test, so it screens.", 0),
    (None, 4.20, None, "gen:conclusion-b",
     "MRI is the sensitive one, so it confirms.", 0),
    # the line the whole thing has been walking towards; it is set large in the
    # picture, so the caption bar stays empty and only the voice carries it
    (None, 5.60, None, "gen:coda",
     ("", "Five minutes and a hamburger set. That is the whole screening test."), 0),
]


# Points in the master a shot must not run into: its red wipes, and the cuts
# where it moves on to something else. The read window is ss .. ss+dur-hold+XFADE
# -- the dissolve tail is real master too, which is how a wipe crept back in
# after a caption got longer -- so check_stops() measures the whole window.
# Measured as the first frame holding a full-width flat non-white row. The
# wipes lead with a navy band and only turn red later, so timing them off the
# red is 0.3s too late -- which is exactly how one crept back into the cut.
MASTER_STOPS = (
    (157.10, "wipe after the equipment shot"),
    (197.80, "cut from the ordering run to the figures"),
    (203.55, "wipe between the hand and eye figures"),
    (210.75, "wipe after the eye figure"),
)


def check_stops():
    """Fail loudly if any shot reads past something it must not show."""
    for ss, dur_s, _, overlay, cap, hold in SEG:
        if ss is None or overlay == "raw":
            continue
        end = ss + dur_s - hold + XFADE
        for at, what in MASTER_STOPS:
            if ss < at < end:
                raise SystemExit(
                    f"shot at {ss} runs to {end:.2f} and crosses {at} ({what}); "
                    f"shorten it or add {end - at:.2f}s of hold")


# The step figures run from the title down to the bottom row of kiosks. Filling
# the frame from the standard crop cut that bottom row off, so they are fitted
# to their own extent instead -- which is nearly the whole frame anyway.
FIG_CROP = (24, 66, 1820, 868)

# The subtitle-free demo is 3840x2160 and 16:9, so the only crop it needs is
# the one that makes it 1280x620 -- taken mostly off the bottom, which holds
# the participant's legs and the base of the kiosk.
RAW_CROP = (0, 40, 3840, 1860)


def ground(seg):
    """Whether a shot sits on the master's footage or on a white field."""
    ov = seg[3] or ""
    return "white" if (ov.startswith("fig:") or ov.startswith("gen:")) else "footage"


def transition(a, b):
    """(seconds, ffmpeg xfade name) for the join between two shots.

    Inside the ordering run the camera never moves and only the instruction
    bubble changes, so a long dissolve there prints one instruction on top of
    the next and neither can be read -- those get a near-cut. Between two shots
    that both sit on white, going through white keeps two blocks of text off
    each other -- except where the next shot is the last one with something
    added, which should look like the addition and nothing else.
    """
    if (a[3], b[3]) == ("gen:conclusion", "gen:conclusion-b"):
        # same picture plus one more card: a flash would read as a new slide
        return 0.12, "fade"
    ga, gb = ground(a), ground(b)
    if ga == gb == "footage":
        return (0.10, "fade") if (a[2] and b[2]) else (0.25, "fade")
    return 0.32, "fadewhite"


def wrap(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def src_overlay():
    return Image.new("RGBA", (SRC_W, SRC_H), (0, 0, 0, 0))


def figure_overlay(title, path):
    """White patches over the Korean captions, English drawn in their place."""
    over = src_overlay()
    d = ImageDraw.Draw(over)
    d.rectangle([690, 74, 1230, 152], fill=(255, 255, 255, 255))
    d.text((960 - d.textlength(title, font=f_title) / 2, 82), title, font=f_title, fill=NAVY + (255,))
    d.rectangle([300, 182, 1810, 244], fill=(255, 255, 255, 255))
    for i, cx in enumerate((425, 683, 938, 1193, 1447, 1702)):
        label = f"Step {i + 1}"
        d.text((cx - d.textlength(label, font=f_step) / 2, 190), label, font=f_step, fill=NAVY + (255,))
    d.rectangle([56, 398, 296, 462], fill=(255, 255, 255, 255))
    d.text((86, 412), "Healthy control", font=f_row, fill=GREEN + (255,))
    d.rectangle([56, 696, 296, 800], fill=(255, 255, 255, 255))
    d.text((86, 708), "Mild cognitive", font=f_row, fill=OLIVE + (255,))
    d.text((86, 742), "impairment", font=f_row, fill=OLIVE + (255,))
    over.save(path)


THREE_BOXES = (          # (x0, y0, x1, y1) in the master, one per figure
    ("Hand movement", (86, 74, 720, 410)),
    ("Eye movement", (86, 424, 720, 762)),
)
# Korean inside each box, in master coordinates: title, the step-number row,
# the group gutter, and (task box only) the two figures.
THREE_KO = (
    ((283, 80, 522, 116), (180, 126, 690, 152), (103, 162, 176, 392)),
    ((283, 429, 522, 465), (180, 475, 690, 501), (103, 492, 176, 716)),
)
THREE_STEP_CX = (220, 306, 389, 474, 558, 643)
# Row centres in the master: healthy on top, impaired below, in each figure box.
THREE_ROWS = ((212, 333), (554, 660))
_three_cache = {}


def three_still(src):
    """The three signal boxes, relaid out so the group names have room.

    Side by side the master's own layout is a portrait column in a landscape
    frame, and the gutter it names its two rows in is 73px wide -- too narrow
    for the English. So each box is cut out separately and placed on a fresh
    canvas with a label column beside it, where the names actually fit. A
    legend on its own was no good: nothing inside the boxes is colour-coded,
    so a green square by itself says nothing about which row is which.
    """
    if "im" in _three_cache:
        return _three_cache["im"]
    still = f"{WORK}/three_src.png"
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", "218.5", "-i", src,
                    "-frames:v", "1", "-y", still], check=True)
    master = Image.open(still).convert("RGB")

    f_t = ImageFont.truetype(BD, 29)
    f_n = ImageFont.truetype(SB, 18)
    crops = []
    for idx, (title, box) in enumerate(THREE_BOXES):
        crop = master.crop(box)
        cd = ImageDraw.Draw(crop)
        ox, oy = box[0], box[1]
        ko_title, ko_steps, ko_gutter = THREE_KO[idx]
        cd.rectangle([ko_title[0] - ox, ko_title[1] - oy, ko_title[2] - ox, ko_title[3] - oy],
                     fill=(255, 255, 255))
        cd.text((403 - ox - cd.textlength(title, font=f_t) / 2, ko_title[1] - oy + 2),
                title, font=f_t, fill=NAVY)
        if ko_steps:
            cd.rectangle([ko_steps[0] - ox, ko_steps[1] - oy, ko_steps[2] - ox, ko_steps[3] - oy],
                         fill=(255, 255, 255))
            cy = (ko_steps[1] + ko_steps[3]) / 2 - oy
            for n, cx in enumerate(THREE_STEP_CX):
                lab = f"Step {n + 1}"
                cd.text((cx - ox - cd.textlength(lab, font=f_n) / 2, cy - 11), lab,
                        font=f_n, fill=NAVY)
        if ko_gutter:
            cd.rectangle([ko_gutter[0] - ox, ko_gutter[1] - oy,
                          ko_gutter[2] - ox, ko_gutter[3] - oy], fill=(255, 255, 255))
        crops.append(crop)

    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    d = ImageDraw.Draw(im)
    fig_w, fig_x = 520, 215
    k = fig_w / crops[0].width
    tops = (18, 320)
    for n in (0, 1):
        h = round(crops[n].height * k)
        im.paste(crops[n].resize((fig_w, h), Image.LANCZOS), (fig_x, tops[n]))
    # The master frames this one like the other two, but it holds two short
    # lines and at that size the empty box read as a mistake, so it is redrawn
    # to its content instead of cropped.
    f_bt = ImageFont.truetype(BD, 24)
    f_bv = ImageFont.truetype(SB, 24)
    bx0, by0, bx1, by1 = 812, 232, 1180, 382
    cx = (bx0 + bx1) / 2
    d.rectangle([bx0, by0, bx1, by1], outline=NAVY, width=2)
    title = "Task performance"
    tw = d.textlength(title, font=f_bt)
    d.rectangle([cx - tw / 2 - 14, by0 - 3, cx + tw / 2 + 14, by0 + 3], fill=PAPER_BG)
    d.text((cx - tw / 2, by0 - 16), title, font=f_bt, fill=NAVY)
    for n, line in enumerate(("1 minute on task", "3 errors")):
        d.text((cx - d.textlength(line, font=f_bv) / 2, by0 + 46 + n * 40),
               line, font=f_bv, fill=(110, 122, 180))

    f_g = ImageFont.truetype(SB, 23)
    for n in (0, 1):
        oy = THREE_BOXES[n][1][1]
        for row, (label, colour) in zip(THREE_ROWS[n],
                                        (("Healthy control", GREEN),
                                         ("Mild cognitive|impairment", OLIVE))):
            cy = tops[n] + (row - oy) * k
            lines = label.split("|")
            y = cy - len(lines) * 15
            for line in lines:
                d.text((200 - d.textlength(line, font=f_g), y), line, font=f_g, fill=colour)
                y += 30
    _three_cache["im"] = im
    return im


def pill_overlay(path):
    """A split screen does not say which half to read, so these do.

    They stay up for all of it rather than just the opening -- whoever starts
    watching in the middle needs them as much as whoever started at the top.
    """
    over = Image.new("RGBA", (W, VID_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for text, right in (("The participant", False), ("What they see", True)):
        tw = d.textlength(text, font=f_pill)
        x0, y0 = (W - 44 - tw - 52) if right else 44, 20
        d.rounded_rectangle([x0 - 2, y0 - 2, x0 + tw + 54, y0 + 56], radius=29,
                            fill=(255, 255, 255, 90))
        d.rounded_rectangle([x0, y0, x0 + tw + 52, y0 + 54], radius=27, fill=(17, 27, 36, 242))
        d.text((x0 + 26, y0 + 10), text, font=f_pill, fill=(255, 255, 255, 255))
    over.save(path)


def bubble_overlay(text, path):
    """A speech bubble sized to what it says.

    The earlier cut took the ordering run from the broadcast master, where a
    Korean instruction bubble is burned into the picture, so this had to be a
    patch big enough to hide it -- which made it far larger than its own text
    needed. The subtitle-free export has no bubble at all, so this one is drawn
    to fit, anchored under the top-right of the participant's half with its tail
    pointing back at them.
    """
    over = Image.new("RGBA", (W, VID_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    lines = []
    for para in text.split("\n"):
        lines += wrap(d, para, f_bub, 330)
    if len(lines) > 3:
        raise SystemExit(f"bubble needs {len(lines)} lines: {text!r}")
    tw = max(d.textlength(line, font=f_bub) for line in lines)
    bw = max(232, tw + 56)
    bh = len(lines) * 50 + 40
    x1, y0 = 616, 26
    x0, y1 = x1 - bw, y0 + bh
    d.polygon([(x0 + 44, y1 - 6), (x0 + 122, y1 - 6), (x0 + 10, y1 + 62)],
              fill=BUBBLE + (255,))
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=BUBBLE + (255,))
    y = y0 + 20
    for line in lines:
        d.text((x0 + (bw - d.textlength(line, font=f_bub)) / 2, y), line,
               font=f_bub, fill=BUBBLE_TX + (255,))
        y += 50
    over.save(path)


def ease(x):
    """Ease-out cubic, clamped."""
    x = 0.0 if x < 0 else (1.0 if x > 1 else x)
    return 1 - (1 - x) ** 3


def rounded_bar(d, x0, y0, x1, y1, fill):
    """A bar with 4px rounded ends, drawn flush to the baseline at x0."""
    if x1 - x0 < 2:
        return
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=fill + (255,))


def draw_results(progress):
    """Accuracy from Table 5, one bar per condition, values counted up.

    One measure on one axis from zero, three bars, every one directly
    labelled -- so colour is never the only thing telling them apart.
    """
    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    d = ImageDraw.Draw(im)
    f_h = ImageFont.truetype(BD, 38)
    f_sub = ImageFont.truetype(SB, 22)
    f_lab = ImageFont.truetype(SB, 30)
    f_lab_b = ImageFont.truetype(BD, 30)
    f_val = ImageFont.truetype(BD, 34)
    f_met = ImageFont.truetype(SB, 21)

    d.text((90, 38), "Telling the two groups apart", font=f_h, fill=INK)
    d.text((90, 92), COHORT, font=f_sub, fill=MUTED)
    d.line([90, 138, 1190, 138], fill=LINE, width=2)

    x0, x1 = 380, 1040    # the track stops here; values live to its right
    for i, (label, acc, spec, sens, f1, colour) in enumerate(RESULTS):
        p = progress[i]
        y = 176 + i * 140
        strong = i == len(RESULTS) - 1
        d.text((90, y + 2), label, font=f_lab_b if strong else f_lab,
               fill=INK if strong else BODY)
        d.rounded_rectangle([x0, y, x1, y + 38], radius=4, fill=TRACK)
        rounded_bar(d, x0, y, x0 + (x1 - x0) * acc / 100 * p, y + 38, colour)
        if p > 0.02:
            val = f"{acc * p:.1f}%"
            d.text((1190 - d.textlength(val, font=f_val), y + 3), val, font=f_val,
                   fill=INK if strong else BODY)
            # :g so each figure reads as the paper prints it -- 90, 87.5, 100
            met = f"specificity {spec:g}   ·   sensitivity {sens:g}   ·   F1 {f1:g}"
            d.text((x0, y + 50), met, font=f_met, fill=MUTED)
    return im


def draw_conclusion(t, second=True):
    """Why each modality is used where -- the paper's two-stage conclusion."""
    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    d = ImageDraw.Draw(im)
    f_h = ImageFont.truetype(BD, 38)
    f_name = ImageFont.truetype(BD, 29)
    f_big = ImageFont.truetype(BD, 82)
    f_met = ImageFont.truetype(SB, 26)
    f_job = ImageFont.truetype(SB, 26)
    f_use = ImageFont.truetype(BD, 26)

    d.text((90, 40), "Two tests, two jobs", font=f_h, fill=INK)
    cards = (
        (90, VR_H, "VR biomarkers", "90.0%", "specificity", "Rules healthy people out.",
         "Screening — under 5 minutes", 0.15),
        (660, MRI_H, "MRI biomarkers", "90.9%", "sensitivity", "Catches the cases.",
         "Confirmation — in the clinic", 0.15),
    )
    for n, (x, colour, name, big, metric, job, use, delay) in enumerate(cards):
        if n and not second:
            continue
        # by the second shot the VR card is already on screen and must not move
        # or re-fade; only the MRI card arrives
        p = 1.0 if (second and n == 0) else ease((t - delay) / 0.55)
        if p <= 0.01:
            continue
        y = 120 + int((1 - p) * 26)
        card = Image.new("RGB", (530, 430), SOFT)
        cd = ImageDraw.Draw(card)
        cd.rectangle([0, 0, 530, 6], fill=colour)
        cd.text((36, 44), name, font=f_name, fill=colour)
        cd.text((36, 96), big, font=f_big, fill=INK)
        cd.text((36, 200), metric, font=f_met, fill=BODY)
        cd.line([36, 250, 494, 250], fill=LINE, width=2)
        cd.text((36, 274), job, font=f_job, fill=BODY)
        cd.text((36, 336), use, font=f_use, fill=colour)
        im.paste(Image.blend(Image.new("RGB", (530, 430), PAPER_BG), card, p), (x, y))
    return im


CODA = ("Five minutes and a hamburger set.", "That is the whole screening test.")


def draw_coda(t):
    """The line the rest of it has been walking towards."""
    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    d = ImageDraw.Draw(im)
    f_big = ImageFont.truetype(BD, 46)
    p = ease(t / 0.8)
    y = 258 + int((1 - p) * 16)
    layer = Image.new("RGB", (W, 160), PAPER_BG)
    ld = ImageDraw.Draw(layer)
    # BOTH_H, not VR_H: the coda is the frame the three demo films have in
    # common, and this rule was the only part of it drawn in a different blue
    ld.rectangle([(W - 96) // 2, 0, (W + 96) // 2, 5], fill=BOTH_H)
    for n, line in enumerate(CODA):
        ld.text(((W - ld.textlength(line, font=f_big)) / 2, 44 + n * 58), line,
                font=f_big, fill=INK if n == 0 else BODY)
    im.paste(Image.blend(Image.new("RGB", (W, 160), PAPER_BG), layer, p), (0, y - 44))
    return im


def arrow(d, x0, y0, x1, y1, colour, width=7, head=17):
    import math
    a = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * math.cos(a), y1 - head * math.sin(a)
    d.line([x0, y0, bx, by], fill=colour, width=width)
    d.polygon([(x1, y1),
               (bx - head * 0.62 * math.sin(a), by + head * 0.62 * math.cos(a)),
               (bx + head * 0.62 * math.sin(a), by - head * 0.62 * math.cos(a))], fill=colour)


MODEL_CHIPS = 0.10       # the chips lead; the rest waits for its word
MODEL_CUES = [1.6, 3.0]
MODEL_SIGNALS = ("Hand movement", "Eye movement", "Task performance")


def draw_model(t):
    """Three signals in, one model, two groups out.

    Redrawn rather than cut from the master, whose version of this shot paints
    the healthy group a third green and the impaired group a second yellow --
    the two figures before it have already given those groups a colour, and a
    reader following the colour loses the thread when it changes. The scatter
    there was a generic illustration of a classifier, not the study's own data,
    so nothing is lost by saying the same thing in the film's own palette.
    """
    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    d = ImageDraw.Draw(im)
    # the model box, so the feed arrows can be aimed at its actual left face
    BOX = (446, 235, 300, 150)
    f_chip = ImageFont.truetype(SB, 25)
    f_box = ImageFont.truetype(BD, 30)
    f_sub = ImageFont.truetype(SB, 21)
    f_out = ImageFont.truetype(BD, 27)

    p2, p3 = (ease((t - c) / 0.55) for c in MODEL_CUES)

    for n, label in enumerate(MODEL_SIGNALS):
        q = ease((t - MODEL_CHIPS - n * 0.16) / 0.5)
        if q <= 0.01:
            continue
        y = 168 + n * 96
        x = 74 - int((1 - q) * 22)
        chip = Image.new("RGB", (286, 66), PAPER_BG)
        cd = ImageDraw.Draw(chip)
        cd.rounded_rectangle([0, 0, 285, 65], radius=8, outline=NAVY, width=2, fill=SOFT)
        cd.text((143 - cd.textlength(label, font=f_chip) / 2, 18), label, font=f_chip, fill=NAVY)
        im.paste(Image.blend(Image.new("RGB", (286, 66), PAPER_BG), chip, q), (x, y))
        if p2 > 0.05:
            # aimed at three points down the box's left face, not straight
            # across -- the top and bottom chips sit outside the box's height,
            # so a horizontal arrow from them lands in empty space
            x0, y0 = 368, y + 33
            x1, y1 = BOX[0] - 4, BOX[1] + 37 + n * 38
            arrow(d, x0, y0, x0 + (x1 - x0) * p2, y0 + (y1 - y0) * p2,
                  (150, 160, 168), 5, 14)

    if p2 > 0.01:
        box = Image.new("RGB", BOX[2:], PAPER_BG)
        bd_ = ImageDraw.Draw(box)
        bd_.rounded_rectangle([0, 0, BOX[2] - 1, BOX[3] - 1], radius=10, fill=VR_H)
        for n, line in enumerate(("Support vector", "machine")):
            bd_.text((150 - bd_.textlength(line, font=f_box) / 2, 30 + n * 38), line,
                     font=f_box, fill=(255, 255, 255))
        bd_.text((150 - bd_.textlength("54 participants", font=f_sub) / 2, 108),
                 "54 participants", font=f_sub, fill=(214, 226, 242))
        im.paste(Image.blend(Image.new("RGB", (300, 150), PAPER_BG), box, p2), BOX[:2])

    if p3 > 0.01:
        for label, colour, cy in (("Healthy control", GREEN, 196),
                                  ("Mild cognitive impairment", OLIVE, 404)):
            arrow(d, BOX[0] + BOX[2] + 10, 310,
                  BOX[0] + BOX[2] + 10 + int(88 * p3), 310 + int((cy - 310) * p3),
                  (110, 120, 128), 6, 15)
            w = 372
            chip = Image.new("RGB", (w, 62), PAPER_BG)
            cd = ImageDraw.Draw(chip)
            cd.rounded_rectangle([1, 1, w - 2, 60], radius=8, fill=SOFT,
                                 outline=colour, width=3)
            cd.text((w / 2 - cd.textlength(label, font=f_out) / 2, 16), label,
                    font=f_out, fill=colour)
            im.paste(Image.blend(Image.new("RGB", (w, 62), PAPER_BG), chip, p3), (850, cy - 31))
    return im


def render_generated(name, dur, path, fps=30):
    """Render a built beat frame by frame and pipe it straight into ffmpeg."""
    n = int(round(dur * fps))

    def frame(t):
        if name == "results":
            return draw_results([ease((t - c) / 0.9) for c in BAR_CUES])
        if name == "conclusion":
            return draw_conclusion(t, second=False)
        if name == "conclusion-b":
            return draw_conclusion(t)
        if name == "three":
            # held still on purpose: a slow push-in was tried and looked wrong,
            # because this is a diagram on a white field, not a photograph --
            # drifting it just makes the boxes creep off their own margins
            return three_still(find_source())
        if name == "coda":
            return draw_coda(t)
        if name == "model":
            return draw_model(t)
        raise SystemExit("unknown generated beat: " + name)

    proc = subprocess.Popen(
        [FF, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{VID_H}", "-framerate", str(fps), "-i", "-",
         "-vf", f"pad={W}:{H}:0:0:color=0x111b24", "-c:v", "libx264", "-crf", "20",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps), "-y", path],
        stdin=subprocess.PIPE)
    for i in range(n):
        proc.stdin.write(frame(i / fps).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed on generated beat " + name)


def caption_bar(text, path):
    im = Image.new("RGBA", (W, BAR_H), BAR_BG + (255,))
    d = ImageDraw.Draw(im)
    if not text:
        im.save(path)
        return
    # one line, always: a second line halves the picture's breathing room and
    # the shots are cut long enough that two shorter captions read better than
    # one long one
    lines = wrap(d, text, f_cap, W - 140)
    if len(lines) > 1:
        raise SystemExit(f"caption needs {len(lines)} lines: {text}")
    y = (BAR_H - len(lines) * 34) // 2
    for line in lines:
        d.text(((W - d.textlength(line, font=f_cap)) / 2, y), line, font=f_cap, fill=(255, 255, 255, 255))
        y += 34
    im.save(path)


def duration(path):
    # ffmpeg writes this to stderr and exits non-zero when given no output file;
    # decode defensively because the console codepage here is not UTF-8.
    res = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    out = (res.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        raise SystemExit("no duration for " + path + ":\n" + out[-400:])
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def find_raw():
    for path in RAW_CANDIDATES:
        if os.path.exists(path):
            return path
    raise SystemExit("subtitle-free demo not found; tried:\n  " + "\n  ".join(RAW_CANDIDATES))


def find_source():
    for path in SRC_CANDIDATES:
        if os.path.exists(path):
            return path
    raise SystemExit("master not found; tried:\n  " + "\n  ".join(SRC_CANDIDATES))


def cap_parts(cap):
    """A caption is one string, or (what the bar shows, what the voice says)."""
    return cap if isinstance(cap, tuple) else (cap, cap)


def caption_groups():
    """Segment index -> (caption, seconds until the next caption starts)."""
    groups = []
    for i, (_, dur, _, _, cap, _) in enumerate(SEG):
        if cap is not None:
            groups.append([i, cap, 0.0])
        groups[-1][2] += dur
    return groups


def main():
    check_stops()
    os.chdir(ROOT)
    src = find_source()
    raw_src = find_raw()
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for f in glob.glob(os.path.join(WORK, "*")):
        os.remove(f)

    pill_overlay(f"{WORK}/pill.png")

    groups = caption_groups()
    for gi, (i, cap, _) in enumerate(groups):
        caption_bar(cap_parts(cap)[0], f"{WORK}/c{gi}.png")
    voiced = [gi for gi, (_, cap, _) in enumerate(groups) if cap_parts(cap)[1]]

    marks = {}

    async def speak():
        for gi in voiced:
            line = cap_parts(groups[gi][1])[1]
            # word boundaries, so a shot can be cut to the words themselves
            comm = edge_tts.Communicate(line, VOICE, rate=RATE, boundary="WordBoundary")
            at = []
            with open(f"{WORK}/r{gi}.mp3", "wb") as fh:
                async for part in comm.stream():
                    if part["type"] == "audio":
                        fh.write(part["data"])
                    elif part["type"] == "WordBoundary":
                        at.append((part["offset"] / 1e7,
                                   part.get("duration", 0) / 1e7, part["text"]))
            marks[gi] = at
    asyncio.run(speak())
    for gi in voiced:
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", f"{WORK}/r{gi}.mp3",
                        "-af", "silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-45dB",
                        "-y", f"{WORK}/n{gi}.mp3"], check=True)

    starts, seg_start, t = [], [], 0.0
    for _, dur_s, *_ in SEG:
        seg_start.append(t)
        t += dur_s
    total = t

    ok = True
    for gi, (i, cap, gdur) in enumerate(groups):
        if not cap_parts(cap)[1]:
            continue
        start = seg_start[i] + LEAD
        d = duration(f"{WORK}/n{gi}.mp3")
        over = start + d > seg_start[i] + gdur
        ok &= not over
        starts.append(start)
        print(f"n{gi}: {seg_start[i]:5.1f}-{seg_start[i] + gdur:5.1f}  voice {d:5.2f} "
              f"ends {start + d:5.2f}  {'OVERRUNS' if over else 'ok'}")
    print(f"total {total:.1f}s | {'all fit' if ok else 'SHORTEN A CAPTION'}")
    if not ok:
        raise SystemExit(1)

    # Cut the built beats to the words that name them, so a chart is never
    # finished while the sentence naming it is still going.
    def cue(gi, words, fallback):
        at = marks.get(gi, [])
        if len(at) < 2:
            return list(fallback)
        # the trim takes silence off both ends, so the words are rescaled onto
        # what is left rather than used raw
        d = duration(f"{WORK}/n{gi}.mp3")
        lo = at[0][0]
        span = at[-1][0] + at[-1][1] - lo
        out = []
        for word, back in zip(words, fallback):
            hit = next((o for o, _, w in at if w.strip(".,").lower() == word), None)
            out.append(round(LEAD + (o_ - lo) / span * d, 2) if (o_ := hit) else back)
        print("  " + " ".join(f"{w}@{o - lo:.2f}" for o, _, w in at))
        return out

    for gi, (i, _, _) in enumerate(groups):
        kind = SEG[i][3]
        if kind == "gen:results":
            BAR_CUES[:] = cue(gi, ("vr", "mri", "together"), BAR_CUES)
            print(f"bar cues: {BAR_CUES}")
        elif kind == "gen:model":
            MODEL_CUES[:] = cue(gi, ("model", "sorts"), MODEL_CUES)
            print(f"model cues: {MODEL_CUES}")

    for i, (ss, dur_s, bubble, overlay, _, hold) in enumerate(SEG):
        if overlay and overlay.startswith("gen:"):
            render_generated(overlay[4:], dur_s + XFADE, f"{WORK}/s{i}.mp4")
            continue
        # Overlays that sit on the master go on before the crop, in master
        # coordinates; the pill is drawn on the finished 1280x620 picture.
        # (path, enable window in this shot's own time); None = always on
        raw = overlay == "raw"
        # pre goes on in source coordinates, before the crop -- that is only for
        # patches that have to land on the master's own figures. post goes on the
        # finished 1280x620 picture, where the bubbles and pills are authored.
        pre, post = [], []
        if raw:
            end = ss + dur_s + XFADE
            for n, (b0, b1, text) in enumerate(BUBBLES):
                if b1 <= ss or b0 >= end:
                    continue
                bubble_overlay(text, f"{WORK}/b{i}_{n}.png")
                # half-open: ffmpeg's between() takes both ends, so without the
                # gap the frame on a boundary draws two bubbles at once and the
                # taller one pokes out from under the shorter
                post.append((f"{WORK}/b{i}_{n}.png",
                             (max(0.0, b0 - ss),
                              min(dur_s + XFADE, b1 - ss) - 0.02)))
        if overlay and overlay.startswith("fig:"):
            figure_overlay(overlay[4:], f"{WORK}/f{i}.png")
            pre.append((f"{WORK}/f{i}.png", None))
        if raw:
            # the pills stay up for the whole split screen: they name which half
            # is which, and that is worth knowing at any point in the run, not
            # only for whoever is watching at the start
            post.append((f"{WORK}/pill.png", None))

        # every shot carries XFADE of real source past its own end, for the
        # dissolve to eat; no shot needs a frozen tail any more
        ins = ["-ss", str(ss), "-t", str(round(dur_s - hold + XFADE, 3)),
               "-i", raw_src if raw else src]
        for path, _ in pre + post:
            ins += ["-i", path]

        chain, last = [], "0:v"
        for n, (_, win) in enumerate(pre):
            gate = "" if win is None else f":enable='between(t,{win[0]:.2f},{win[1]:.2f})'"
            chain.append(f"[{last}][{n + 1}:v]overlay=0:0{gate}[p{n}]")
            last = f"p{n}"
        if raw:
            # 4K and 16:9 with nothing burned in, so the only crop is the one
            # that makes it the picture's shape
            chain.append(f"[{last}]crop={RAW_CROP[2]}:{RAW_CROP[3]}:{RAW_CROP[0]}:{RAW_CROP[1]},"
                         f"scale={W}:{VID_H},setsar=1[b]")
        elif overlay and overlay.startswith("fig:"):
            chain.append(f"[{last}]crop={FIG_CROP[2]}:{FIG_CROP[3]}:{FIG_CROP[0]}:{FIG_CROP[1]},"
                         f"scale={W}:{VID_H}:force_original_aspect_ratio=decrease,"
                         f"pad={W}:{VID_H}:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1[b]")
        else:
            chain.append(f"[{last}]crop={SRC_W}:{CROP_H}:0:0,scale=-2:{VID_H},"
                         f"crop={W}:{VID_H},setsar=1[b]")
        last = "b"
        for n, (_, win) in enumerate(post):
            k = len(pre) + n + 1
            gate = "" if win is None else f":enable='between(t,{win[0]:.2f},{win[1]:.2f})'"
            chain.append(f"[{last}][{k}:v]overlay=0:0{gate}[q{n}]")
            last = f"q{n}"
        tail = f"tpad=stop_mode=clone:stop_duration={hold:.3f}," if hold else ""
        chain.append(f"[{last}]{tail}pad={W}:{H}:0:0:color=0x111b24[v]")

        subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins,
                        "-filter_complex", ";".join(chain),
                        "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "24", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-r", "30", "-t", str(round(dur_s + XFADE, 3)), "-y",
                        f"{WORK}/s{i}.mp4"], check=True)

    ins = []
    for i in range(len(SEG)):
        ins += ["-i", f"{WORK}/s{i}.mp4"]
    for gi in range(len(groups)):
        ins += ["-i", f"{WORK}/c{gi}.png"]
    chain, last = [], "0:v"
    for i in range(1, len(SEG)):
        d_x, kind = transition(SEG[i - 1], SEG[i])
        chain.append(f"[{last}][{i}:v]xfade=transition={kind}:duration={d_x}:"
                     f"offset={seg_start[i]:.3f}[x{i}]")
        last = f"x{i}"
    for gi, (i, _, gdur) in enumerate(groups):
        t0 = seg_start[i]
        chain.append(f"[{last}][{len(SEG) + gi}:v]overlay=0:H-{BAR_H}:"
                     f"enable='between(t,{t0:.2f},{t0 + gdur:.2f})'[k{gi}]")
        last = f"k{gi}"
    # a simple -vf cannot be mixed with a complex graph, so the closing fade is
    # the last node of the graph itself
    chain.append(f"[{last}]fade=t=out:st={total - 0.9:.2f}:d=0.9:color=white[out]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins,
                    "-filter_complex", ";".join(chain), "-map", "[out]",
                    "-c:v", "libx264", "-crf", "24", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-r", "30", "-t", str(total), "-y",
                    f"{WORK}/captioned.mp4"], check=True)

    ins = ["-i", f"{WORK}/captioned.mp4"]
    for gi in voiced:
        ins += ["-i", f"{WORK}/n{gi}.mp3"]
    filt, labels = [], []
    for n, start in enumerate(starts):
        filt.append(f"[{n + 1}:a]adelay={int(start * 1000)}:all=1,aresample=48000[a{n}]")
        labels.append(f"[a{n}]")
    filt.append("".join(labels) + f"amix=inputs={len(voiced)}:normalize=0:dropout_transition=0,apad[aout]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-t", str(total), "-y", OUT], check=True)

    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", "7", "-i", OUT,
                    "-frames:v", "1", "-y", f"{WORK}/poster.png"], check=True)
    Image.open(f"{WORK}/poster.png").save(POSTER, "WEBP", quality=86, method=6)
    print(f"built {duration(OUT):.1f}s  {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
