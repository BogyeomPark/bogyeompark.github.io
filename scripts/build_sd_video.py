"""Build the self-disclosure demo video: picture, narration and the timing
between them.

The film shows the experiment, not the interface. An earlier cut ran one
chatbot's transcript on its own and described the control condition in a
caption; that version could not show the study's only independent variable,
because the variable is a difference between two conversations and only one of
them was on screen. Both run here, side by side, asking the same questions.

The result is in the picture before any number is: the control finishes and goes
quiet while the disclosing side is still talking. That gap is the engagement
finding - 10.6 minutes against 17.5 - and it reads without being narrated.

Numbers are from the CHI EA 2025 paper (Park, Park and Seo; n = 40, randomly
assigned). The transcripts are the study's protocol shortened, not participant
logs: the disclosures are verbatim from the protocol, the student replies stand
in for what students wrote. The measures on the results panel are real.

There is no screen recorder here and no headless browser, so the video is drawn
rather than captured: PIL renders every frame and ffmpeg encodes them. Shapes
are drawn oversized and downsampled, because PIL has no antialiasing of its own
and the jagged version reads as a diagram of a chatbot instead of a chatbot.

The narration is spoken first and the picture is cut to fit it. Each beat runs
for as long as its line takes to say, or as long as its messages take to play,
whichever is longer - so the beat list, not a frame count, is what to edit.

Usage:
  python scripts/build_sd_video.py          # narration, video, poster, thumb
"""

import asyncio
import hashlib
import json
import math
import os
import re
import subprocess
import sys

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "assets", "demos", "self-disclosure")
WORK = os.path.join(ROOT, "tmp", "sd_build")
OUT = os.path.join(DEMO, "demo.mp4")
POSTER = os.path.join(DEMO, "poster.webp")
THUMB = os.path.join(DEMO, "thumb.webp")
CAPS = os.path.join(ROOT, "tmp", "sd_caps.json")
FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1280, 720
FPS = 30                        # 30, like the other two demo films
BAR_H = 100                     # caption bar, same as the kiosk film
SS = 4                          # supersampling for the icons, drawn once and cached
MS = 2                          # supersampling for everything else drawn as shapes

VOICE, RATE = "en-US-AriaNeural", "-15%"     # same voice and pace as the kiosk film
TYPE_LEAD = 0.7                 # typing indicator before each bot message
READ = 0.045                    # seconds on screen per character of message text
FLOOR = 1.4                     # shortest hold, so one-liners do not flash
LEAD = 0.3                      # caption is up this long before the voice starts
TAIL = 0.9                      # quiet after a line before the caption changes

# The voice pads every clip with about a second of silence at each end. Left in,
# it counts as speech when the beat is timed and then shows up as a gap, so each
# clip is trimmed back to the words before anything is measured.
TRIM = ("silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,"
        "areverse,silenceremove=start_periods=1:start_silence=0.10:start_threshold=-45dB,"
        "areverse")

INK = (23, 37, 42)
BODY = (70, 87, 92)
MUTED = (102, 120, 125)
FAINT = (152, 167, 172)
LINE = (223, 231, 233)
PAPER = (255, 255, 255)
SOFT = (245, 249, 249)
FIELD = (243, 247, 249)
ACCENT = (31, 66, 117)
WARM = (181, 93, 62)
WARM_BG = (253, 246, 243)
# The two conditions. Navy is the site's primary and the one that reads as
# the better outcome, which is what the disclosing condition is; the control
# takes the neutral grey. Warm stays behind, marking the disclosed sentences
# themselves inside the transcript - a highlighter, not a condition.
GREY = (139, 154, 159)
COND = (31, 66, 117)
TRACK = (237, 242, 245)
BAR_BG = (17, 27, 36)

F = lambda p, s: ImageFont.truetype(p, s)
UI = r"C:\Windows\Fonts\segoeui.ttf"
UI_SB = r"C:\Windows\Fonts\seguisb.ttf"
UI_B = r"C:\Windows\Fonts\segoeuib.ttf"

f_msg = F(UI, 18)
f_win = F(UI_SB, 17)
f_sub = F(UI, 14)
f_field = F(UI, 15)
f_cap = F(UI_B, 27)
f_row = F(UI_SB, 19)
f_val = F(UI_B, 25)
f_note = F(UI, 15)
f_kick = F(UI_SB, 14)
f_chip = F(UI_SB, 16)
f_panel = F(UI_B, 26)
f_coda = F(UI_B, 46)

# (who, text, disclosure). Same inventory on both sides; the right-hand chatbot
# answers each item about itself before it asks. Everything marked disclosure is
# from the study's protocol.
LEFT = [
    ("bot", "Hello! What is your name?", False),
    ("user", "I'm Bogyeom.", False),
    ("bot", "These are the eight main causes of academic stress. Which one applies to you?", False),
    ("user", "Assignment overload.", False),
    ("bot", "Have you had any of these? Sleep problems, fatigue, headaches, stomach trouble.", False),
    ("user", "Sleep problems.", False),
    ("bot", "And how do you usually cope with it?", False),
    ("user", "I just push through.", False),
]
RIGHT = [
    ("bot", "Hello! What is your name?", False),
    ("user", "I'm Bogyeom.", False),
    ("bot", "Actually, I have something on my mind. I study consistently, but I can't retain "
            "what I read, and my grades never reflect the effort.", True),
    ("user", "That happens to me too, honestly.", False),
    ("bot", "These are the eight main causes of academic stress. Mine is the academic workload. "
            "What about you?", False),
    ("user", "Assignment overload. And there is never enough time.", False),
    ("bot", "As exams get closer I have more and more trouble falling asleep, and I go in "
            "already tired.", True),
    ("bot", "Have you had any of these? Sleep problems, fatigue, headaches, stomach trouble.", False),
    ("user", "I barely sleep the week before an exam.", False),
    ("bot", "When it piles up I end up telling a friend about it, and that usually helps.", True),
    ("bot", "And how do you usually cope with it?", False),
    ("user", "Complaining to my roommate, more than I would admit.", False),
]

# A rung is one step of the inventory: what the left plays and what the right
# plays, started at the same instant. Both sides wait for the slower one before
# the next rung begins, because the whole comparison is two answers to one
# question and it only reads if they arrive together. Letting each side run at
# its own pace put the left's question beside the right's small talk.
RUNGS = [
    ([0, 1], [0, 1]),        # the opening, identical on both sides
    ([], [2, 3]),            # the right discloses; the left has nothing here
    ([2], [4]),              # stressors, asked
    ([3], [5]),              # stressors, answered
    ([], [6]),               # the right discloses again
    ([4], [7]),              # symptoms, asked
    ([5], [8]),              # symptoms, answered
    ([], [9]),               # and again
    ([6], [10]),             # coping, asked
    ([7], [11]),             # coping, answered
]

# One beat per spoken line. A chat beat names the turns each side plays during
# it, so a side with nothing to play sits still - which is the point at beat two,
# and again at the end, where the control has finished and the other has not.
BEATS = [
    {"line": "Forty students, split in two. Both chatbots asked the same questions.",
     "rungs": [0]},
    {"line": "The one on the right goes first. It says what applies to itself, then asks.",
     "rungs": [1]},
    # One fact per line. Three of these used to say "and again, the same thing"
    # over three different areas of the inventory - true, and dull to listen to,
    # because the picture was already making that point on its own. Each line
    # now carries something the picture cannot: the rule, the protocol, the
    # size of what is left at the end.
    {"line": "Same question, both at once \u2014 give an answer first and you get a longer one back.",
     "rungs": [2, 3]},
    {"line": "It says it can't sleep before exams, before it asks whether you can.",
     "rungs": [4]},
    {"line": "The student on the right keeps giving more than the question asked for.",
     "rungs": [5, 6]},
    {"line": "The disclosures are fixed. Every one is written into the study's protocol.",
     "rungs": [7]},
    {"line": "By the end, one of these conversations is half again the size of the other.",
     "rungs": [8, 9], "least": 7.0},
    {"line": "Sessions ran seven minutes longer. Students wrote a hundred words more.",
     "rows": 2},
    {"line": "Scored against the questionnaire: right half the time, instead of a third.",
     "rows": 3},
    {"line": "And two and a half times as much of the talk reached a plan of action.",
     "rows": 4},
    # the line the rest of it has been walking towards; it is set large in the
    # picture, so the caption bar stays empty and only the voice carries it.
    # It ends on what the student found rather than on what to build, because
    # the site opens by claiming this work finds a person’s blind spots and
    # this is the study that actually shows one being found - the paper’s own
    # words are "uncovered previously overlooked stressors"
    {"line": "One sentence about itself, first. And the student names a stressor they had missed.",
     "coda": True, "cap": "", "least": 6.5},
]

CODA = ("One sentence about itself, first.",
        "And the student names a stressor they had missed.")

# CHI EA 2025, Tables 2 and 3 and the self-reflection distribution in 4.3.
RESULTS = [
    ("Session length", 10.62, 17.54, "10.6 min", "17.5 min", "p < .001"),
    ("Words the student wrote", 161.83, 259.65, "162", "260", "p < .001"),
    ("Assessment accuracy", 0.35, 0.52, "0.35", "0.52", "p < .05"),
    ("Talk that reached a plan of action", 2.40, 6.01, "2.4%", "6.0%", "not tested"),
]
PAD = 18
AV = 30
TYPING_H = 34
GAP = 12
ROW_H = 25                                       # message line height
WIN_W = 596
WIN_Y0, WIN_Y1 = 26, H - BAR_H - 14              # the windows own the picture now
WIN_L = (22, WIN_Y0, 22 + WIN_W, WIN_Y1)
WIN_R = (W - 22 - WIN_W, WIN_Y0, W - 22, WIN_Y1)
HEAD_H = 46
CMP_H = 44
CMP_Y = WIN_Y1 - CMP_H
VIEW_TOP = WIN_Y0 + HEAD_H + 8
VIEW_BOT = CMP_Y - 6
VIEW_W = WIN_W
VIEW_H = VIEW_BOT - VIEW_TOP
PANEL = (22, WIN_Y0, W - 22, WIN_Y1)             # the results panel


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


def measure(draw, turns):
    """Lay a transcript out once; frames then just pick a scroll offset."""
    laid, y = [], 0
    for who, text, disc in turns:
        max_w = 400 if who == "bot" else 340
        lines = wrap(draw, text, f_msg, max_w - 2 * 15)
        h = len(lines) * ROW_H + 2 * 13
        laid.append({"who": who, "disc": disc, "lines": lines, "w": max_w, "h": h, "y": y})
        y += h + GAP
    return laid


def content_height(laid, shown, typing):
    end = (laid[shown - 1]["y"] + laid[shown - 1]["h"]) if shown else 0
    return end + GAP + TYPING_H if typing else end


def hold_of(item):
    return max(FLOOR, READ * sum(len(l) for l in item["lines"]))


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def ease(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def duration(path):
    # ffmpeg writes this to stderr and exits non-zero when given no output file;
    # decode defensively because the console codepage here is not UTF-8.
    res = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    out = (res.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        raise SystemExit("no duration for " + path + ":\n" + out[-400:])
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


# ------------------------------------------------------------------ icons ---
# Drawn once at SS scale and shrunk, which is the only antialiasing available
# here. At 30px a jagged circle is the difference between an interface and a
# clip-art sticker.

def bot_icon(size, colour):
    """A robot head - aerial, ears, two eyes, a smile. It has to read as 'bot'
    at 30px, which two earlier marks did not: an abstract face read as an alien,
    and the same head in the warm tone read as a jack-o'-lantern."""
    n = size * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = lambda v: v * n
    d.rectangle([u(.455), u(.02), u(.545), u(.20)], fill=colour)
    d.ellipse([u(.38), u(.00), u(.62), u(.13)], fill=colour)
    d.rounded_rectangle([u(.00), u(.44), u(.13), u(.72)], radius=u(.05), fill=colour)
    d.rounded_rectangle([u(.87), u(.44), u(1.0), u(.72)], radius=u(.05), fill=colour)
    d.rounded_rectangle([u(.11), u(.19), u(.89), u(.97)], radius=u(.15), fill=colour)
    for cx in (.33, .67):
        d.ellipse([u(cx - .10), u(.38), u(cx + .10), u(.58)], fill=PAPER)
    d.arc([u(.31), u(.52), u(.69), u(.82)], 20, 160, fill=PAPER, width=int(u(.06)))
    return im.resize((size, size), Image.LANCZOS)


def user_icon(size):
    """Head and shoulders, clipped to the circle - the human side of the thread."""
    n = size * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = lambda v: v * n
    d.rectangle([0, 0, n, n], fill=ACCENT)
    d.ellipse([u(.35), u(.20), u(.65), u(.50)], fill=PAPER)
    d.rounded_rectangle([u(.21), u(.56), u(.79), u(1.06)], radius=u(.29), fill=PAPER)
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    im.putalpha(mask)
    return im.resize((size, size), Image.LANCZOS)


def send_icon(size):
    n = size * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = lambda v: v * n
    d.ellipse([0, 0, n - 1, n - 1], fill=(211, 220, 224))
    d.polygon([(u(.29), u(.28)), (u(.75), u(.50)), (u(.29), u(.72)), (u(.41), u(.50))], fill=PAPER)
    return im.resize((size, size), Image.LANCZOS)


BOT_AV = bot_icon(AV, ACCENT)
USER_AV = user_icon(AV)
HEAD_AV = bot_icon(26, ACCENT)
SEND_AV = send_icon(30)


# -------------------------------------------------------------- furniture ---

def window(b, box, colour):
    x0, y0, x1, y1 = box
    s = lambda *v: [x * MS for x in v]
    b.rounded_rectangle(s(x0 + 3, y0 + 5, x1 + 3, y1 + 5), radius=16 * MS, fill=(236, 242, 243))
    b.rounded_rectangle(s(*box), radius=16 * MS, fill=PAPER, outline=LINE, width=1 * MS)
    b.line(s(x0 + 1, y0 + HEAD_H, x1 - 1, y0 + HEAD_H), fill=LINE, width=1 * MS)
    b.line(s(x0 + 1, y0 + (y1 - y0) - CMP_H, x1 - 1, y0 + (y1 - y0) - CMP_H), fill=LINE, width=1 * MS)
    b.rounded_rectangle(s(x0 + 16, CMP_Y + 9, x1 - 52, y1 - 9), radius=13 * MS, fill=FIELD,
                        outline=LINE, width=1 * MS)
    b.rounded_rectangle(s(x1 - 152, y0 + 14, x1 - 16, y0 + 34), radius=10 * MS, fill=colour)


def build_base(scene):
    """Everything that never moves. Cached per scene, so the per-frame work is
    only the messages or the bars."""
    if scene == "card":
        return Image.new("RGB", (W, H), PAPER)
    big = Image.new("RGB", (W * MS, H * MS), SOFT)
    b = ImageDraw.Draw(big)
    if scene == "chat":
        window(b, WIN_L, GREY)
        window(b, WIN_R, COND)
    else:
        s = lambda *v: [x * MS for x in v]
        b.rounded_rectangle(s(PANEL[0] + 3, PANEL[1] + 5, PANEL[2] + 3, PANEL[3] + 5),
                            radius=16 * MS, fill=(236, 242, 243))
        b.rounded_rectangle(s(*PANEL), radius=16 * MS, fill=PAPER, outline=LINE, width=1 * MS)

    im = big.resize((W, H), Image.LANCZOS)
    if scene != "chat":
        return im

    d = ImageDraw.Draw(im)
    # the control pill is a light grey, so its label is ink rather than white:
    # white on that grey is 2.6:1 and unreadable at 14px
    for box, title, note, tag, tint in (
            (WIN_L, "Asks only", "runs the inventory straight", "CONTROL", INK),
            (WIN_R, "Goes first", "answers each item about itself", "SELF-DISCLOSING", PAPER)):
        x0, y0, x1, _ = box
        im.paste(HEAD_AV, (x0 + 16, y0 + 10), HEAD_AV)
        d.text((x0 + 50, y0 + 6), title, font=f_win, fill=INK)
        d.text((x0 + 50, y0 + 25), note, font=f_sub, fill=MUTED)
        # anchored, not offset by hand: the pill label sat low every other way
        d.text((x1 - 84, y0 + 24), tag, font=f_kick, fill=tint, anchor="mm")
        d.text((x0 + 32, CMP_Y + 13), "Type a reply", font=f_field, fill=FAINT)
        im.paste(SEND_AV, (x1 - 46, CMP_Y + 7), SEND_AV)
    return im


def caption_bar(text):
    im = Image.new("RGB", (W, BAR_H), BAR_BG)
    if not text:
        return im
    d = ImageDraw.Draw(im)
    # one line, always, the same rule the kiosk film runs on: a second line
    # halves the picture’s breathing room, and a beat that needs two lines
    # wants to be two beats
    lines = wrap(d, text, f_cap, W - 140)
    if len(lines) > 1:
        raise SystemExit(f"caption needs {len(lines)} lines: {text}")
    y = (BAR_H - 34) // 2
    d.text(((W - d.textlength(lines[0], font=f_cap)) / 2, y), lines[0], font=f_cap, fill=PAPER)
    return im


# --------------------------------------------------------------- messages ---

def message_layer(laid, shown, typing, offset):
    """Bubbles are drawn oversized and shrunk, then the text goes on at native
    size. The layer is pasted into the window afterwards so a message scrolling
    past the top is cut by the window edge instead of drawn over the border."""
    big = Image.new("RGB", (VIEW_W * MS, VIEW_H * MS), PAPER)
    b = ImageDraw.Draw(big)
    placed = []

    for item in laid[:shown]:
        top = item["y"] - offset
        if top + item["h"] < -50 or top > VIEW_H + 50:
            continue
        if item["who"] == "bot":
            x0 = PAD + AV + 10
            bg = WARM_BG if item["disc"] else SOFT
        else:
            x0 = VIEW_W - PAD - AV - 10 - item["w"]
            bg = ACCENT
        x1, y1 = x0 + item["w"], top + item["h"]
        b.rounded_rectangle([x0 * MS, top * MS, x1 * MS, y1 * MS], radius=13 * MS, fill=bg)
        # one squared corner on the speaker's side: a chat bubble has a tail
        tail = [x0, y1 - 8, x0 + 8, y1] if item["who"] == "bot" else [x1 - 8, y1 - 8, x1, y1]
        b.rectangle([v * MS for v in tail], fill=bg)
        if item["disc"]:
            b.rounded_rectangle([x0 * MS, top * MS, (x0 + 4) * MS, y1 * MS], radius=2 * MS, fill=WARM)
            b.rectangle([x0 * MS, (y1 - 8) * MS, (x0 + 4) * MS, y1 * MS], fill=WARM)
        placed.append((item, top, x0))

    typing_top = content_height(laid, shown, False) + GAP - offset
    if typing:
        x0 = PAD + AV + 10
        b.rounded_rectangle([x0 * MS, typing_top * MS, (x0 + 68) * MS, (typing_top + TYPING_H) * MS],
                            radius=13 * MS, fill=SOFT)
        b.rectangle([x0 * MS, (typing_top + TYPING_H - 8) * MS, (x0 + 8) * MS,
                     (typing_top + TYPING_H) * MS], fill=SOFT)
        for i in range(3):
            lift = max(0.0, math.sin((typing / FPS * 1.5 - i * 0.13) * 2 * math.pi))
            cx, cy, r = x0 + 20 + i * 14, typing_top + 17 - lift * 3.0, 3.8
            b.ellipse([(cx - r) * MS, (cy - r) * MS, (cx + r) * MS, (cy + r) * MS],
                      fill=mix(LINE, MUTED, lift))

    im = big.resize((VIEW_W, VIEW_H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for item, top, x0 in placed:
        fg = PAPER if item["who"] == "user" else (INK if item["disc"] else BODY)
        y = top + 13
        for line in item["lines"]:
            d.text((x0 + 15, y), line, font=f_msg, fill=fg)
            y += ROW_H
        if item["who"] == "bot":
            im.paste(BOT_AV, (int(x0 - AV - 10), int(top + 3)), BOT_AV)
        else:
            im.paste(USER_AV, (int(x0 + item["w"] + 10), int(top + 3)), USER_AV)
    if typing:
        im.paste(BOT_AV, (PAD, int(typing_top + 2)), BOT_AV)
    return im


def done_stamp(d, box):
    """A window whose conversation has ended says so where a chat client would
    say it - in the composer. It used to sit under the last message, which was
    free space when the transcript hung from the top of the window and is the
    last message now that it hangs from the bottom."""
    x0, _, x1, y1 = box
    d.rounded_rectangle([x0 + 19, CMP_Y + 12, x1 - 55, y1 - 12], radius=11, fill=FIELD)
    d.text(((x0 + x1 - 36) / 2, CMP_Y + 22), "conversation ended", font=f_field,
           fill=FAINT, anchor="mm")


# ---------------------------------------------------------------- results ---

def results_layer(progress):
    """Four measures, each a pair of bars. progress is one 0-1 value per row."""
    im = Image.new("RGB", (PANEL[2] - PANEL[0], PANEL[3] - PANEL[1]), PAPER)
    d = ImageDraw.Draw(im)
    inner_w = PANEL[2] - PANEL[0]

    d.text((56, 30), "40 students, randomly assigned", font=f_panel, fill=INK)
    d.text((56, 66), "CHI EA 2025", font=f_note, fill=FAINT)
    x = inner_w - 470
    for colour, label in ((GREY, "Asks only"), (COND, "Goes first")):
        d.rounded_rectangle([x, 36, x + 26, 48], radius=6, fill=colour)
        d.text((x + 36, 42), label, font=f_row, fill=BODY, anchor="lm")
        x += 240

    bar_x, bar_w = 380, inner_w - 380 - 150
    y = 108
    for i, (name, a, bv, a_txt, b_txt, test) in enumerate(RESULTS):
        p = progress[i]
        # every row keeps its label and an empty track from the first frame:
        # revealing the rows one at a time left the panel looking half built for
        # most of the time it was on screen. The track then fades to white as the
        # bar fills it, so the shorter bar’s value is not left sitting on a
        # length that is not its own - which read as the two values being set
        # against different backs
        d.text((56, y + 8), name, font=f_row, fill=INK if p > 0.001 else MUTED)
        for k in range(2):
            d.rounded_rectangle([bar_x, y + k * 36, bar_x + bar_w, y + k * 36 + 26],
                                radius=6, fill=mix(TRACK, PAPER, ease(p)))
        if p <= 0.001:
            y += 118
            continue
        # the p-value sat in 15px grey under the label and nobody saw it; a chip
        # is the smallest thing that reads as a statement rather than a footnote
        tw = d.textlength(test, font=f_chip)
        d.rounded_rectangle([56, y + 38, 56 + tw + 26, y + 66], radius=14,
                            fill=(234, 239, 241))
        d.text((69, y + 52), test, font=f_chip, fill=BODY, anchor="lm")

        top = max(a, bv)
        for k, (value, text, colour) in enumerate(((a, a_txt, GREY), (bv, b_txt, COND))):
            by = y + k * 36
            width = max(3, int(bar_w * (value / top) * ease(p)))
            d.rounded_rectangle([bar_x, by, bar_x + width, by + 26], radius=6, fill=colour)
            # the value rides the end of its own bar out, rather than appearing
            # once the bar has stopped
            d.text((bar_x + width + 16, by + 13), text, font=f_val,
                   fill=INK if k else MUTED, anchor="lm")
        y += 118
    return im


def card_frame():
    return Image.new("RGB", (W, H - BAR_H), PAPER)


def coda_layer(t):
    im = card_frame()
    p = ease(t / 0.8)
    y = 258 + int((1 - p) * 16)
    layer = Image.new("RGB", (W, 160), PAPER)
    ld = ImageDraw.Draw(layer)
    ld.rectangle([(W - 96) // 2, 0, (W + 96) // 2, 5], fill=COND)
    for i, line in enumerate(CODA):
        ld.text(((W - ld.textlength(line, font=f_coda)) / 2, 44 + i * 58), line,
                font=f_coda, fill=INK if i == 0 else BODY)
    im.paste(Image.blend(Image.new("RGB", (W, 160), PAPER), layer, p), (0, y - 44))
    return im


# ------------------------------------------------------------------ timing ---

def narrate(lines):
    """Speak each beat, then trim the silence off it. Clips are named after a
    hash of voice, rate and text, so editing one line re-records that line and
    leaves the rest alone."""
    os.makedirs(WORK, exist_ok=True)
    clips, todo = [], []
    for line in lines:
        key = hashlib.sha1(f"{VOICE}|{RATE}|{line}".encode("utf-8")).hexdigest()[:12]
        clip = os.path.join(WORK, f"v{key}.wav")
        clips.append(clip)
        if not os.path.exists(clip):
            todo.append((line, os.path.join(WORK, f"v{key}.mp3"), clip))

    async def speak():
        for line, raw, _ in todo:
            await edge_tts.Communicate(line, VOICE, rate=RATE).save(raw)

    if todo:
        print(f"recording {len(todo)} of {len(lines)} lines")
        asyncio.run(speak())
        for _, raw, clip in todo:
            subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", raw,
                            "-af", TRIM, "-y", clip], check=True)
    return clips, [duration(c) for c in clips]


def side_frames(laid, turns):
    """Frames a side needs to play the turns it owns in a rung."""
    total = 0
    for i in turns:
        if laid[i]["who"] == "bot":
            total += int(FPS * TYPE_LEAD)
        total += int(FPS * hold_of(laid[i]))
    return total


def rung_frames(left, right, i):
    """A rung lasts as long as its slower side."""
    l, r = RUNGS[i]
    return max(side_frames(left, l), side_frames(right, r))


def plan(left, right, durations):
    out = []
    for beat, spoken in zip(BEATS, durations):
        need = max(int(FPS * (LEAD + spoken + TAIL)), int(FPS * beat.get("least", 0)))
        play = sum(rung_frames(left, right, i) for i in beat.get("rungs", []))
        out.append({"beat": beat, "frames": max(need, play), "spoken": spoken})
    return out


def side_track(laid, turns, frames, start_shown):
    """Per-frame (shown, typing, idle) for one side of one rung. Once its turns
    are played the side sits still, which is the point at the rungs the control
    has nothing to fill - it waits there while the other one discloses."""
    track, shown = [], start_shown
    for i in turns:
        if laid[i]["who"] == "bot":
            for tick in range(int(FPS * TYPE_LEAD)):
                track.append((shown, tick + 1, False))
        shown = i + 1
        for _ in range(int(FPS * hold_of(laid[i]))):
            track.append((shown, 0, False))
    while len(track) < frames:
        track.append((shown, 0, True))
    return track[:frames], shown


def build_specs(left, right, beats):
    specs = []
    l_shown = r_shown = 0
    rows_seen = 0
    for step in beats:
        beat, n = step["beat"], step["frames"]
        line = beat["line"]
        cap = beat.get("cap", line)
        if "rungs" in beat:
            l_track, r_track = [], []
            for i in beat["rungs"]:
                span = rung_frames(left, right, i)
                l_part, l_shown = side_track(left, RUNGS[i][0], span, l_shown)
                r_part, r_shown = side_track(right, RUNGS[i][1], span, r_shown)
                l_track += l_part
                r_track += r_part
            while len(l_track) < n:
                l_track.append((l_shown, 0, True))
                r_track.append((r_shown, 0, True))
            for k in range(n):
                specs.append({"scene": "chat", "cap": cap,
                              "l": l_track[k][:2], "r": r_track[k][:2],
                              # one flag for both windows: the control settles
                              # about a second before the other and stamping each
                              # side as it lands read as a stutter rather than an
                              # ending. Per frame, not per beat - l_shown is past
                              # the end by the time the beat is built, so a side
                              # idling mid-beat was being stamped as finished
                              "ended": (l_track[k][2] and l_track[k][0] == len(left)
                                        and r_track[k][2] and r_track[k][0] == len(right))})
        elif beat.get("coda"):
            for k in range(n):
                specs.append({"scene": "card", "cap": cap, "t": k / FPS})
        else:
            want = beat["rows"]
            for k in range(n):
                rows = []
                for i in range(len(RESULTS)):
                    if i < rows_seen:
                        rows.append(1.0)
                    elif i < want:
                        rows.append(min(1.0, max(0.0, (k / FPS - (i - rows_seen) * 0.35) / 0.55)))
                    else:
                        rows.append(0.0)
                specs.append({"scene": "results", "cap": cap, "rows": tuple(rows)})
            rows_seen = want
    return specs


# ------------------------------------------------------------------- build ---

def render(left, right, specs):
    bases = {s: build_base(s) for s in {"chat", "results", "card"}}
    bars = {spec["cap"]: caption_bar(spec["cap"]) for spec in specs}
    poster_at = max(i for i, s in enumerate(specs) if s["cap"] == BEATS[6]["line"])
    poster_png = os.path.join(WORK, "poster.png")
    video = os.path.join(WORK, "video.mp4")

    proc = subprocess.Popen(
        [FF, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
         "-crf", "25", "-preset", "slow", "-pix_fmt", "yuv420p", "-y", video],
        stdin=subprocess.PIPE)

    scroll = {"l": None, "r": None}
    for n, spec in enumerate(specs):
        im = bases[spec["scene"]].copy()
        d = ImageDraw.Draw(im)
        if spec["scene"] == "chat":
            for key, laid, box in (("l", left, WIN_L), ("r", right, WIN_R)):
                shown, typing = spec[key]
                # ease towards the bottom of the transcript instead of snapping
                # to it: a chat window scrolls, and the jump is the tell
                target = content_height(laid, shown, typing)
                if scroll[key] is None:
                    scroll[key] = target
                scroll[key] += (target - scroll[key]) * 0.3
                # no floor at zero: a short transcript sits on the composer the
                # way a real one does, instead of stranding the window half empty
                offset = round((scroll[key] - VIEW_H) * MS) / MS
                im.paste(message_layer(laid, shown, typing, offset), (box[0], VIEW_TOP))
                if spec["ended"]:
                    done_stamp(d, box)
        elif spec["scene"] == "results":
            im.paste(results_layer(spec["rows"]), (PANEL[0], PANEL[1]))
        else:
            im.paste(coda_layer(spec["t"]), (0, 0))
        im.paste(bars[spec["cap"]], (0, H - BAR_H))
        proc.stdin.write(im.tobytes())
        if n == poster_at:
            im.save(poster_png)
        if n % 200 == 0:
            print(f"  {n}/{len(specs)}")

    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed on the picture")
    return video, poster_png


def mux(video, clips, starts, total):
    ins = ["-i", video]
    for clip in clips:
        ins += ["-i", clip]
    filt, labels = [], []
    for i, start in enumerate(starts):
        filt.append(f"[{i + 1}:a]adelay={int(start * 1000)}:all=1,aresample=48000[a{i}]")
        labels.append(f"[a{i}]")
    filt.append("".join(labels) + f"amix=inputs={len(clips)}:normalize=0:dropout_transition=0,apad[out]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins,
                    "-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[out]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                    "-t", str(round(total, 3)), "-y", OUT], check=True)


def main():
    # the console here is cp949, and two of the lines carry an em dash
    sys.stdout.reconfigure(errors="replace")
    os.makedirs(WORK, exist_ok=True)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    left, right = measure(probe, LEFT), measure(probe, RIGHT)
    clips, durations = narrate([b["line"] for b in BEATS])
    beats = plan(left, right, durations)
    specs = build_specs(left, right, beats)

    at, caps = 0, []
    print(f"{len(specs)} frames -> {len(specs) / FPS:.2f}s")
    for step in beats:
        quiet = step["frames"] / FPS - LEAD - step["spoken"]
        caps.append({"t": round(at / FPS, 2), "cap": step["beat"]["line"]})
        print(f"  {at / FPS:6.2f}s  {step['frames'] / FPS:5.2f}s window, "
              f"{step['spoken']:5.2f}s spoken, {quiet:4.2f}s quiet   {step['beat']['line'][:44]}")
        at += step["frames"]

    video, poster_png = render(left, right, specs)
    mux(video, clips, [c["t"] + LEAD for c in caps], len(specs) / FPS)

    poster = Image.open(poster_png).convert("RGB")
    poster.save(POSTER, "WEBP", quality=86, method=6)
    poster.resize((1024, 576), Image.LANCZOS).save(THUMB, "WEBP", quality=86, method=6)
    with open(CAPS, "w", encoding="utf-8") as fh:
        json.dump(caps, fh, ensure_ascii=False, indent=1)
    print(f"built {duration(OUT):.1f}s  {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
