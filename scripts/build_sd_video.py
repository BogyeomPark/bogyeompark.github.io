"""Render the self-disclosure demo video frame by frame.

There is no screen recorder here and no headless browser, so the video is drawn
rather than captured: PIL renders every frame of the conversation and ffmpeg
encodes them. That turns out to be the better tool anyway - the timing is exact
and reproducible, and the same script re-runs if the wording changes.

The window is drawn to look like a chat client someone would actually be sitting
in front of - a bot avatar, a typing indicator, replies keyed into a composer
before they are sent, a view that scrolls rather than jumping - because the claim
being illustrated is about what it is like to talk to this thing. Shapes are
drawn oversized and downsampled: PIL has no antialiasing of its own, and the
jagged version reads as a diagram of a chatbot instead of a chatbot.

The conversation is the study's SD protocol, shortened to fit under a minute.
Disclosures keep their warm tint here for the same reason they have it in the
live demo: they are the independent variable, and a viewer who cannot pick them
out of the transcript has not been shown anything.

Frame counts are load-bearing. The narration is mixed separately against the
caption times in tmp/sd_caps.json, so anything that changes a hold moves the
captions and the audio has to be rebuilt with it.

Usage:
  python scripts/build_sd_video.py          # mp4 + poster frame, no audio
  (narration is generated separately and muxed in by the caller)
"""

import math
import os
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MP4 = os.path.join(ROOT, "tmp", "sd-video-only.mp4")
OUT_POSTER = os.path.join(ROOT, "tmp", "sd-poster.png")
FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1280, 720
FPS = 24
BAR_H = 86                      # caption bar, same proportion as the other demo video
SS = 4                          # supersampling for the icons, drawn once and cached
MS = 2                          # supersampling for everything else drawn as shapes

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
BAR_BG = (17, 27, 36)
LIVE = (46, 143, 105)

F = lambda p, s: ImageFont.truetype(p, s)
UI = r"C:\Windows\Fonts\segoeui.ttf"
UI_SB = r"C:\Windows\Fonts\seguisb.ttf"
UI_B = r"C:\Windows\Fonts\segoeuib.ttf"

f_msg = F(UI, 21)
f_head = F(UI_SB, 19)
f_status = F(UI, 15)
f_small = F(UI, 17)
f_field = F(UI, 18)
f_cap = F(UI_B, 27)
f_rep_h = F(UI_SB, 23)
f_rep = F(UI, 19)
f_rail = F(UI, 18)
f_rail_b = F(UI_SB, 18)
f_rail_h = F(UI_SB, 13)

# (who, text, disclosure) - who is 'bot' or 'user'
TURNS = [
    ("bot", "Hello! What is your name?", False),
    ("user", "I'm Bogyeom.", False),
    ("bot", "Nice to meet you, Bogyeom. How was your day?", False),
    ("user", "Long. Three deadlines landed in the same week.", False),
    ("bot", "Actually, I came here today because I have something on my mind. Despite studying consistently, "
            "I find it hard to retain what I read, and my grades never reflect the effort. It is disheartening.", True),
    ("user", "That happens to me too, honestly.", False),
    ("bot", "I looked into it, and these are the eight main causes of academic stress. I think mine is the "
            "academic workload. What about you?", False),
    ("user", "Assignment overload. And there is never enough time.", False),
    ("bot", "As exam dates approach I have more and more trouble falling asleep, and I go in already tired.", True),
    ("bot", "Have you had any of these? Sleep disorders, chronic fatigue, headaches, digestive problems.", False),
    ("user", "I barely sleep the week before an exam.", False),
]

# caption index -> caption shown from that turn onward
CAPTIONS = {
    0: "A chatbot that assesses academic stress. It opens like any other.",
    4: "Then it says something about itself \u2014 before it has asked anything.",
    6: "Only then does it ask. Every list arrives after its own disclosure.",
    8: "It says it cannot sleep, before asking whether you can.",
    10: "The control condition asked identical questions, with every disclosure removed.",
}
REPORT_CAPTION = "At the end the conversation itself is scored \u2014 nobody fills in a form."
CLOSING_CAPTION = "Students talking to the disclosing version named their stressors more clearly."

REPORT = [
    ("Causes", ["Assignment overload", "Limited time", "Academic workload"]),
    ("Symptoms", ["Sleep disorders", "Chronic fatigue"]),
    ("Coping strategies", ["Venting emotions and confiding in others"]),
]
REPORT_TITLE = "Scored from the conversation \u2014 SISCO Inventory of Academic Stress"

# The five areas of the SISCO inventory, shown as a rail beside the chat. It is
# not decoration: the whole design of the SD condition is that each area is
# opened by a disclosure, and a viewer who cannot see the areas cannot see that.
STAGES = ["Opening", "Stressors", "Physical", "Psychological", "Behavioural", "Coping"]
STAGE_AT = {0: 0, 6: 1, 8: 2}          # turn index -> stage index

PAD = 26
AV = 38                                          # avatar size
TYPING_H = 38
GAP = 14                                         # space between bubbles
RAIL = (44, 34, 268, H - BAR_H - 26)             # stage rail bounds
CARD = (296, 34, W - 44, H - BAR_H - 26)         # chat window bounds
HEAD_H = 60                                      # window title bar
CMP_H = 58                                       # composer
CMP_Y = CARD[3] - CMP_H
SEND = (CARD[2] - 56, CMP_Y + 11, CARD[2] - 20, CMP_Y + 47)
FIELD_BOX = (CARD[0] + 20, CMP_Y + 11, SEND[0] - 12, CMP_Y + 47)
VIEW_TOP = CARD[1] + HEAD_H + 10
VIEW_BOT = CMP_Y - 6
VIEW_W = CARD[2] - CARD[0]
VIEW_H = VIEW_BOT - VIEW_TOP


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
    """Lay the transcript out once; frames then just pick a scroll offset."""
    laid, y = [], 0
    for who, text, disc in turns:
        max_w = 590 if who == "bot" else 470
        lines = wrap(draw, text, f_msg, max_w - 2 * 18)
        h = len(lines) * 29 + 2 * 15
        laid.append({"who": who, "disc": disc, "lines": lines, "w": max_w, "h": h, "y": y})
        y += h + GAP
    return laid, y


def content_height(laid, shown, typing):
    end = (laid[shown - 1]["y"] + laid[shown - 1]["h"]) if shown else 0
    return end + GAP + TYPING_H if typing else end


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


# ------------------------------------------------------------------ icons ---
# Drawn once at SS scale and shrunk, which is the only antialiasing available
# here. At 34px a jagged circle is the difference between an interface and a
# clip-art sticker.

def bot_icon(size):
    """A robot head - aerial, ears, two eyes, a smile. It has to read as 'bot'
    at 30px, which the abstract face it replaces did not: without the aerial and
    the ears the same head reads as a jack-o'-lantern, and before that, as an
    alien."""
    n = size * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = lambda v: v * n
    d.rectangle([u(.455), u(.02), u(.545), u(.20)], fill=WARM)
    d.ellipse([u(.38), u(.00), u(.62), u(.13)], fill=WARM)
    d.rounded_rectangle([u(.00), u(.44), u(.13), u(.72)], radius=u(.05), fill=WARM)
    d.rounded_rectangle([u(.87), u(.44), u(1.0), u(.72)], radius=u(.05), fill=WARM)
    d.rounded_rectangle([u(.11), u(.19), u(.89), u(.97)], radius=u(.15), fill=WARM)
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


def send_icon(size, active):
    n = size * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = lambda v: v * n
    d.ellipse([0, 0, n - 1, n - 1], fill=ACCENT if active else (211, 220, 224))
    d.polygon([(u(.29), u(.28)), (u(.75), u(.50)), (u(.29), u(.72)), (u(.41), u(.50))], fill=PAPER)
    return im.resize((size, size), Image.LANCZOS)


BOT_AV = bot_icon(AV)
USER_AV = user_icon(AV)
HEAD_AV = bot_icon(32)
SEND_ON = send_icon(36, True)
SEND_OFF = send_icon(36, False)


# -------------------------------------------------------------- furniture ---

def build_base(stage):
    """Everything that never moves: the rail, the window, the composer. Cached
    per stage, so the per-frame work is only the messages."""
    big = Image.new("RGB", (W * MS, H * MS), SOFT)
    b = ImageDraw.Draw(big)
    s = lambda *v: [x * MS for x in v]

    y = RAIL[1] + 74
    for i in range(len(STAGES)):
        done, now = i < stage, i == stage
        colour = ACCENT if now else (INK if done else LINE)
        if i:
            b.line(s(RAIL[0] + 13, y - 26, RAIL[0] + 13, y - 6), fill=LINE, width=2 * MS)
        r = 9 if now else 6
        b.ellipse(s(RAIL[0] + 13 - r, y - r, RAIL[0] + 13 + r, y + r),
                  fill=colour if (now or done) else PAPER, outline=colour, width=2 * MS)
        y += 46

    b.rounded_rectangle(s(CARD[0] + 3, CARD[1] + 5, CARD[2] + 3, CARD[3] + 5),
                        radius=18 * MS, fill=(236, 242, 243))
    b.rounded_rectangle(s(*CARD), radius=18 * MS, fill=PAPER, outline=LINE, width=1 * MS)
    b.line(s(CARD[0] + 1, CARD[1] + HEAD_H, CARD[2] - 1, CARD[1] + HEAD_H), fill=LINE, width=1 * MS)
    b.line(s(CARD[0] + 1, CMP_Y, CARD[2] - 1, CMP_Y), fill=LINE, width=1 * MS)
    b.rounded_rectangle(s(*FIELD_BOX), radius=18 * MS, fill=FIELD, outline=LINE, width=1 * MS)
    b.ellipse(s(CARD[0] + 62, CARD[1] + 40, CARD[0] + 70, CARD[1] + 48), fill=LIVE)

    im = big.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((RAIL[0] + 4, RAIL[1] + 6), "ACADEMIC STRESS", font=f_rail_h, fill=MUTED)
    d.text((RAIL[0] + 4, RAIL[1] + 26), "INVENTORY", font=f_rail_h, fill=MUTED)
    y = RAIL[1] + 74
    for i, name in enumerate(STAGES):
        now = i == stage
        d.text((RAIL[0] + 34, y - 11), name, font=f_rail_b if now else f_rail,
               fill=INK if i <= stage else MUTED)
        y += 46

    im.paste(HEAD_AV, (CARD[0] + 20, CARD[1] + 15), HEAD_AV)
    d.text((CARD[0] + 62, CARD[1] + 13), "Academic stress chat", font=f_head, fill=INK)
    d.text((CARD[0] + 78, CARD[1] + 35), "Online", font=f_status, fill=MUTED)
    d.text((CARD[2] - 190, CARD[1] + 20), "self-disclosing", font=f_small, fill=WARM)
    return im


def build_report():
    """The score arrives as a message from the bot, not as a slide - it is the
    same window, so it has to look like the same window."""
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    x0, x1 = PAD + AV + 12, VIEW_W - PAD
    title = wrap(probe, REPORT_TITLE, f_rep_h, x1 - x0 - 44)

    h = 20 + len(title) * 30 + 14
    for _, items in REPORT:
        h += 34 + len(items) * 30 + 12
    h += 8

    big = Image.new("RGB", (VIEW_W * MS, VIEW_H * MS), PAPER)
    b = ImageDraw.Draw(big)
    b.rounded_rectangle([x0 * MS, 10 * MS, x1 * MS, (10 + h) * MS], radius=15 * MS,
                        fill=(250, 252, 253), outline=LINE, width=1 * MS)
    b.rectangle([x0 * MS, (h + 1) * MS, (x0 + 9) * MS, (10 + h) * MS], fill=(250, 252, 253))
    im = big.resize((VIEW_W, VIEW_H), Image.LANCZOS)

    d = ImageDraw.Draw(im)
    im.paste(BOT_AV, (PAD, 14), BOT_AV)
    x, y = x0 + 22, 30
    for line in title:
        d.text((x, y), line, font=f_rep_h, fill=INK)
        y += 30
    y += 14
    for name, items in REPORT:
        d.text((x, y), name, font=f_rep_h, fill=ACCENT)
        y += 34
        for item in items:
            d.ellipse([x + 6, y + 8, x + 13, y + 15], fill=WARM)
            d.text((x + 26, y), item, font=f_rep, fill=BODY)
            y += 30
        y += 12
    return im


def caption_bar(text):
    im = Image.new("RGB", (W, BAR_H), BAR_BG)
    d = ImageDraw.Draw(im)
    lines = wrap(d, text, f_cap, W - 140)
    y = (BAR_H - len(lines) * 34) // 2
    for line in lines:
        d.text(((W - d.textlength(line, font=f_cap)) / 2, y), line, font=f_cap, fill=PAPER)
        y += 34
    return im


# --------------------------------------------------------------- messages ---

def message_layer(laid, shown, typing, offset):
    """Bubbles are drawn oversized and shrunk, then the text goes on at native
    size - shrinking the text as well would soften it against the rest of the
    frame. The layer is pasted into the window afterwards so a message scrolling
    past the top is cut by the window edge instead of drawn over the border."""
    big = Image.new("RGB", (VIEW_W * MS, VIEW_H * MS), PAPER)
    b = ImageDraw.Draw(big)
    placed = []

    for item in laid[:shown]:
        top = item["y"] - offset
        if top + item["h"] < -60 or top > VIEW_H + 60:
            continue
        if item["who"] == "bot":
            x0 = PAD + AV + 12
            bg = WARM_BG if item["disc"] else SOFT
        else:
            x0 = VIEW_W - PAD - AV - 12 - item["w"]
            bg = ACCENT
        x1, y1 = x0 + item["w"], top + item["h"]
        b.rounded_rectangle([x0 * MS, top * MS, x1 * MS, y1 * MS], radius=15 * MS, fill=bg)
        # one squared corner on the speaker's side: a chat bubble has a tail
        tail = [x0, y1 - 9, x0 + 9, y1] if item["who"] == "bot" else [x1 - 9, y1 - 9, x1, y1]
        b.rectangle([v * MS for v in tail], fill=bg)
        if item["disc"]:
            b.rounded_rectangle([x0 * MS, top * MS, (x0 + 4) * MS, y1 * MS], radius=2 * MS, fill=WARM)
            b.rectangle([x0 * MS, (y1 - 9) * MS, (x0 + 4) * MS, y1 * MS], fill=WARM)
        placed.append((item, top, x0))

    typing_top = content_height(laid, shown, False) + GAP - offset
    if typing:
        x0 = PAD + AV + 12
        b.rounded_rectangle([x0 * MS, typing_top * MS, (x0 + 76) * MS, (typing_top + TYPING_H) * MS],
                            radius=15 * MS, fill=SOFT)
        b.rectangle([x0 * MS, (typing_top + TYPING_H - 9) * MS, (x0 + 9) * MS,
                     (typing_top + TYPING_H) * MS], fill=SOFT)
        for i in range(3):
            lift = max(0.0, math.sin((typing / FPS * 1.5 - i * 0.13) * 2 * math.pi))
            cx, cy, r = x0 + 22 + i * 16, typing_top + 19 - lift * 3.5, 4.2
            b.ellipse([(cx - r) * MS, (cy - r) * MS, (cx + r) * MS, (cy + r) * MS],
                      fill=mix(LINE, MUTED, lift))

    im = big.resize((VIEW_W, VIEW_H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for item, top, x0 in placed:
        fg = PAPER if item["who"] == "user" else (INK if item["disc"] else BODY)
        y = top + 15
        for line in item["lines"]:
            d.text((x0 + 18, y), line, font=f_msg, fill=fg)
            y += 29
        if item["who"] == "bot":
            im.paste(BOT_AV, (int(x0 - AV - 12), int(top + 4)), BOT_AV)
        else:
            im.paste(USER_AV, (int(x0 + item["w"] + 12), int(top + 4)), USER_AV)
    if typing:
        im.paste(BOT_AV, (PAD, int(typing_top + 2)), BOT_AV)
    return im


def draw_composer(im, d, text):
    x, y = FIELD_BOX[0] + 20, FIELD_BOX[1] + 6
    if text:
        d.text((x, y), text, font=f_field, fill=INK)
        caret = x + d.textlength(text, font=f_field) + 3
        d.rectangle([caret, y + 2, caret + 2, y + 21], fill=ACCENT)
    else:
        d.text((x, y), "Message", font=f_field, fill=FAINT)
    button = SEND_ON if text else SEND_OFF
    im.paste(button, (SEND[0], SEND[1]), button)


def build_specs(laid):
    """One tuple per frame. Kept separate so the count can be checked against
    the narration without rendering anything."""
    specs = []
    caption, stage = CAPTIONS[0], 0
    for index, item in enumerate(laid):
        caption = CAPTIONS.get(index, caption)
        stage = STAGE_AT.get(index, stage)
        # hold long enough to read it, with a floor so short lines do not flash
        hold = int(FPS * max(1.5, 0.055 * sum(len(l) for l in item["lines"])))
        if item["who"] == "bot":
            for tick in range(int(FPS * 0.7)):
                specs.append((index, tick + 1, caption, False, stage, ""))
            for _ in range(hold):
                specs.append((index + 1, 0, caption, False, stage, ""))
        else:
            # the reply is keyed into the composer before it is sent, out of the
            # same hold - the window should behave the way one does when there
            # is a person on this end of it
            keyed = min(int(FPS * 0.8), int(hold * 0.45))
            text = TURNS[index][1]
            for k in range(keyed):
                specs.append((index, 0, caption, False, stage,
                              text[:max(1, round(len(text) * (k + 1) / keyed))]))
            for _ in range(hold - keyed):
                specs.append((index + 1, 0, caption, False, stage, ""))

    for _ in range(int(FPS * 2.2)):
        specs.append((len(laid), 0, CAPTIONS[10], False, stage, ""))
    for _ in range(int(FPS * 5.0)):
        specs.append((len(laid), 0, REPORT_CAPTION, True, len(STAGES) - 1, ""))
    for _ in range(int(FPS * 4.0)):
        specs.append((len(laid), 0, CLOSING_CAPTION, True, len(STAGES) - 1, ""))
    return specs


def main():
    laid, _ = measure(ImageDraw.Draw(Image.new("RGB", (10, 10))), TURNS)
    specs = build_specs(laid)

    bases = {s: build_base(s) for s in sorted({spec[4] for spec in specs})}
    bars = {c: caption_bar(c) for c in {spec[2] for spec in specs}}
    report = build_report()
    poster_at = max(i for i, spec in enumerate(specs) if spec[2] == CAPTIONS[6])

    print(f"{len(specs)} frames -> {len(specs) / FPS:.2f}s")
    proc = subprocess.Popen(
        [FF, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
         "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", "-y", OUT_MP4],
        stdin=subprocess.PIPE)

    scroll = 0.0
    for n, (shown, typing, cap, is_report, stage, typed) in enumerate(specs):
        # ease towards the bottom of the transcript instead of snapping to it:
        # a chat window scrolls, and the jump is the tell that this was drawn
        scroll += (content_height(laid, shown, typing) - scroll) * 0.3
        offset = round(max(0.0, scroll - VIEW_H) * MS) / MS

        im = bases[stage].copy()
        im.paste(report if is_report else message_layer(laid, shown, typing, offset),
                 (CARD[0], VIEW_TOP))
        draw_composer(im, ImageDraw.Draw(im), typed)
        im.paste(bars[cap], (0, H - BAR_H))
        proc.stdin.write(im.tobytes())
        if n == poster_at:
            im.save(OUT_POSTER)
        if n % 200 == 0:
            print(f"  {n}/{len(specs)}")

    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("wrote", OUT_MP4, os.path.getsize(OUT_MP4) // 1024, "KB")


if __name__ == "__main__":
    main()
