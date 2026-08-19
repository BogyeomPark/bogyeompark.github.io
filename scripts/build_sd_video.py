"""Render the self-disclosure demo video frame by frame.

There is no screen recorder here and no headless browser, so the video is drawn
rather than captured: PIL renders every frame of the conversation and ffmpeg
encodes them. That turns out to be the better tool anyway - the timing is exact
and reproducible, and the same script re-runs if the wording changes.

The conversation is the study's SD protocol, shortened to fit under a minute.
Disclosures keep their warm tint here for the same reason they have it in the
live demo: they are the independent variable, and a viewer who cannot pick them
out of the transcript has not been shown anything.

Usage:
  python scripts/build_sd_video.py          # frames + mp4, no audio
  (narration is generated separately and muxed in by the caller)
"""

import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "tmp", "sd_frames")
OUT_MP4 = os.path.join(ROOT, "tmp", "sd-video-only.mp4")

W, H = 1280, 720
FPS = 24
BAR_H = 86                      # caption bar, same proportion as the other demo video

INK = (23, 37, 42)
BODY = (70, 87, 92)
MUTED = (102, 120, 125)
LINE = (223, 231, 233)
PAPER = (255, 255, 255)
SOFT = (245, 249, 249)
ACCENT = (31, 66, 117)
WARM = (181, 93, 62)
WARM_BG = (253, 246, 243)
BAR_BG = (17, 27, 36)

F = lambda p, s: ImageFont.truetype(p, s)
UI = r"C:\Windows\Fonts\segoeui.ttf"
UI_SB = r"C:\Windows\Fonts\seguisb.ttf"
UI_B = r"C:\Windows\Fonts\segoeuib.ttf"

f_msg = F(UI, 21)
f_msg_b = F(UI_SB, 21)
f_head = F(UI_SB, 19)
f_small = F(UI, 17)
f_cap = F(UI_B, 27)
f_rep_h = F(UI_SB, 23)
f_rep = F(UI, 19)

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

PAD = 26
CARD = (96, 34, W - 96, H - BAR_H - 26)          # chat card bounds
VIEW_TOP = CARD[1] + 62
VIEW_BOT = CARD[3] - 24


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
        max_w = 640 if who == "bot" else 520
        lines = wrap(draw, text, f_msg, max_w - 2 * 18)
        h = len(lines) * 29 + 2 * 15
        laid.append({"who": who, "disc": disc, "lines": lines, "w": max_w, "h": h, "y": y})
        y += h + 14
    return laid, y


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_frame(laid, shown, typing, caption, report=False):
    im = Image.new("RGB", (W, H), SOFT)
    d = ImageDraw.Draw(im)

    rounded(d, CARD, 18, PAPER, LINE, 1)
    d.line([(CARD[0] + 1, CARD[1] + 50), (CARD[2] - 1, CARD[1] + 50)], fill=LINE, width=1)
    d.ellipse([CARD[0] + 22, CARD[1] + 16, CARD[0] + 40, CARD[1] + 34], fill=ACCENT)
    d.text((CARD[0] + 52, CARD[1] + 16), "Academic stress chat", font=f_head, fill=INK)
    d.text((CARD[2] - 190, CARD[1] + 19), "self-disclosing", font=f_small, fill=WARM)

    if report:
        draw_report(d)
    else:
        visible = laid[:shown]
        total = (visible[-1]["y"] + visible[-1]["h"]) if visible else 0
        if typing:
            total += 46
        offset = max(0, total - (VIEW_BOT - VIEW_TOP))

        for item in visible:
            top = VIEW_TOP + item["y"] - offset
            if top + item["h"] < VIEW_TOP - 40 or top > VIEW_BOT + 40:
                continue
            if item["who"] == "bot":
                x0 = CARD[0] + PAD
                bg = WARM_BG if item["disc"] else SOFT
                fg = INK if item["disc"] else BODY
            else:
                x0 = CARD[2] - PAD - item["w"]
                bg, fg = ACCENT, PAPER
            box = [x0, top, x0 + item["w"], top + item["h"]]
            rounded(d, box, 15, bg)
            if item["disc"]:
                d.rounded_rectangle([x0, top, x0 + 4, top + item["h"]], radius=2, fill=WARM)
            ty = top + 15
            for line in item["lines"]:
                d.text((x0 + 18, ty), line, font=f_msg, fill=fg)
                ty += 29

        if typing:
            top = VIEW_TOP + total - 46 - offset
            rounded(d, [CARD[0] + PAD, top, CARD[0] + PAD + 74, top + 38], 15, SOFT)
            for i in range(3):
                cx = CARD[0] + PAD + 22 + i * 15
                on = (typing + i) % 3 == 0
                r = 5 if on else 4
                d.ellipse([cx - r, top + 19 - r, cx + r, top + 19 + r],
                          fill=MUTED if on else LINE)

    d.rectangle([0, H - BAR_H, W, H], fill=BAR_BG)
    lines = wrap(d, caption, f_cap, W - 140)
    ty = H - BAR_H + (BAR_H - len(lines) * 34) // 2
    for line in lines:
        tw = d.textlength(line, font=f_cap)
        d.text(((W - tw) / 2, ty), line, font=f_cap, fill=PAPER)
        ty += 34
    return im


def draw_report(d):
    x = CARD[0] + PAD
    y = VIEW_TOP + 4
    d.text((x, y), "Scored from the conversation \u2014 SISCO Inventory of Academic Stress",
           font=f_rep_h, fill=INK)
    y += 44
    for title, items in REPORT:
        d.text((x, y), title, font=f_rep_h, fill=ACCENT)
        y += 34
        for item in items:
            d.ellipse([x + 6, y + 8, x + 13, y + 15], fill=WARM)
            d.text((x + 26, y), item, font=f_rep, fill=BODY)
            y += 30
        y += 12


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for old in os.listdir(OUT_DIR):
        os.remove(os.path.join(OUT_DIR, old))

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    laid, _ = measure(probe, TURNS)

    frames = []
    caption = CAPTIONS[0]
    for index, item in enumerate(laid):
        caption = CAPTIONS.get(index, caption)
        if item["who"] == "bot":
            for tick in range(int(FPS * 0.7)):
                frames.append((index, tick // 4 + 1, caption, False))
        # hold long enough to read it, with a floor so short lines do not flash
        hold = max(1.5, 0.055 * sum(len(l) for l in item["lines"]))
        for _ in range(int(FPS * hold)):
            frames.append((index + 1, 0, caption, False))

    for _ in range(int(FPS * 2.2)):
        frames.append((len(laid), 0, CAPTIONS[10], False))
    for _ in range(int(FPS * 5.0)):
        frames.append((len(laid), 0, REPORT_CAPTION, True))
    for _ in range(int(FPS * 4.0)):
        frames.append((len(laid), 0, CLOSING_CAPTION, True))

    print(f"{len(frames)} frames -> {len(frames) / FPS:.1f}s")
    for n, (shown, typing, cap, report) in enumerate(frames):
        draw_frame(laid, shown, typing, cap, report).save(
            os.path.join(OUT_DIR, f"f{n:05d}.png"), compress_level=1)
        if n % 200 == 0:
            print(f"  {n}/{len(frames)}")

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ff, "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", str(FPS), "-i", os.path.join(OUT_DIR, "f%05d.png"),
        "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p",
        OUT_MP4,
    ], check=True)
    print("wrote", OUT_MP4, os.path.getsize(OUT_MP4) // 1024, "KB")


if __name__ == "__main__":
    main()
