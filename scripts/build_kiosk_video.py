"""Assemble the VR biomarker video: the patient, the measures, the finding.

The figures are the lab's own — the hand-movement traces and the gaze heat maps
from the CHI deck, still animating — with their Korean captions covered and the
same labels drawn in English on top. Redrawing them from scratch was tried and
was wrong: boxes and scribbles are not somebody's data, and the colour in the
gaze map means something.

Sources live in tmp/ (kiosk-raw.mp4, clips/006.mp4) and are not in the repo.
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
W, H, BAR_H = 1280, 720, 100
BAR_BG = (17, 27, 36)
VOICE, RATE = "en-US-AriaNeural", "+0%"
TRIM = 1.65                      # the master fades in from white until 0.87s

SB = r"C:\Windows\Fonts\seguisb.ttf"
BD = r"C:\Windows\Fonts\segoeuib.ttf"
f_cap = ImageFont.truetype(BD, 27)
f_pill = ImageFont.truetype(SB, 22)
f_title = ImageFont.truetype(BD, 46)
f_step = ImageFont.truetype(SB, 34)
f_row = ImageFont.truetype(BD, 32)

# Sampled out of the figure itself rather than guessed, so the English labels
# are the same colours as the series they name.
GREEN, OLIVE, NAVY = (115, 154, 91), (187, 160, 56), (16, 29, 86)

OUT = os.path.join(ROOT, "assets/demos/vr-biomarker/kiosk-playthrough.mp4")
POSTER = os.path.join(ROOT, "assets/demos/vr-biomarker/kiosk-poster.webp")
WORK = os.path.join(ROOT, "tmp/kiosk_build")

SEG = [
    ("vid", "tmp/kiosk-raw.mp4", TRIM, 9.0,
     "A patient orders a hamburger set in virtual reality. Told once, six steps.", "pill"),
    ("vid", "tmp/kiosk-raw.mp4", TRIM + 9.0, 9.0,
     "No notes, no asking again. It is all held in memory while the screen changes.", None),
    ("vid", "tmp/kiosk-raw.mp4", TRIM + 24.0, 9.0,
     "Hand movement, eye movement and task performance are recorded as it happens.", None),
    # clip 006 runs the hand figure to 5.8s, wipes, then the gaze figure from 6.4s
    ("fig", "tmp/clips/006.mp4", 0.8, 5.0,
     "Patients with mild cognitive impairment traced longer, more tangled paths.", "hand"),
    ("fig", "tmp/clips/006.mp4", 6.6, 6.2,
     "Their gaze scattered across the screen instead of settling on the target.", "gaze"),
    ("img", "tmp/panels/result.png", 0, 8.0,
     "Read together, VR and MRI reached ninety four point four percent accuracy.", None),
    ("vid", "tmp/kiosk-raw.mp4", 50.0, 6.0,
     "VR for the first screen. MRI to confirm.", None),
]


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


def figure_overlay(title, path):
    """White patches over the Korean captions, English drawn in their place."""
    over = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    d.rectangle([690, 74, 1230, 152], fill=(255, 255, 255, 255))
    d.text((960 - d.textlength(title, font=f_title) / 2, 82), title, font=f_title, fill=NAVY + (255,))
    d.rectangle([300, 182, 1810, 244], fill=(255, 255, 255, 255))
    for i, cx in enumerate((425, 680, 935, 1190, 1445, 1700)):
        label = f"Step {i + 1}"
        d.text((cx - d.textlength(label, font=f_step) / 2, 190), label, font=f_step, fill=NAVY + (255,))
    d.rectangle([70, 396, 296, 466], fill=(255, 255, 255, 255))
    d.text((78, 410), "Healthy control", font=f_row, fill=GREEN + (255,))
    d.rectangle([70, 694, 296, 806], fill=(255, 255, 255, 255))
    d.text((78, 706), "Mild cognitive", font=f_row, fill=OLIVE + (255,))
    d.text((78, 744), "impairment", font=f_row, fill=OLIVE + (255,))
    over.save(path)


def pill_overlay(path):
    """A split screen does not say which half to read, so the opening does."""
    over = Image.new("RGBA", (W, H - BAR_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for text, cx in (("The participant", 320), ("What they see", 960)):
        tw = d.textlength(text, font=f_pill)
        x0, y0 = cx - tw / 2 - 18, 24
        d.rounded_rectangle([x0, y0, x0 + tw + 36, y0 + 40], radius=20, fill=(17, 27, 36, 215))
        d.text((x0 + 18, y0 + 8), text, font=f_pill, fill=(255, 255, 255, 255))
    over.save(path)


def caption_bar(text, path):
    im = Image.new("RGBA", (W, BAR_H), BAR_BG + (255,))
    d = ImageDraw.Draw(im)
    lines = wrap(d, text, f_cap, W - 140)
    if len(lines) > 2:
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


def main():
    os.chdir(ROOT)
    os.makedirs(WORK, exist_ok=True)
    for f in glob.glob(os.path.join(WORK, "*")):
        os.remove(f)

    pill_overlay(f"{WORK}/pill.png")
    figure_overlay("Hand movement", f"{WORK}/hand.png")
    figure_overlay("Gaze, as a heat map", f"{WORK}/gaze.png")

    for i, (kind, src, ss, dur_s, cap, extra) in enumerate(SEG):
        caption_bar(cap, f"{WORK}/c{i}.png")
        head = (["-loop", "1", "-t", str(dur_s), "-i", src] if kind == "img"
                else ["-ss", str(ss), "-t", str(dur_s), "-i", src])
        ins = head + ["-i", f"{WORK}/c{i}.png"]
        if extra:
            ins += ["-i", f"{WORK}/{extra}.png"]
        if kind == "fig":
            fc = ("[0:v][2:v]overlay=0:0[lab];"
                  f"[lab]scale={W}:{H - BAR_H}:force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:0:color=0xffffff,setsar=1[b];"
                  f"[b][1:v]overlay=0:H-{BAR_H}[v]")
        else:
            fc = (f"[0:v]scale={W}:{H - BAR_H}:force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:0:color=0xf5f9f9,setsar=1[b];")
            fc += (f"[b][2:v]overlay=0:0[p];[p][1:v]overlay=0:H-{BAR_H}[v]" if extra
                   else f"[b][1:v]overlay=0:H-{BAR_H}[v]")
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins, "-filter_complex", fc,
                        "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "28", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-r", "30", "-t", str(dur_s), "-y",
                        f"{WORK}/s{i}.mp4"], check=True)

    with open(f"{WORK}/list.txt", "w") as fh:
        for i in range(len(SEG)):
            fh.write(f"file 's{i}.mp4'\n")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", f"{WORK}/list.txt", "-c", "copy", "-y", f"{WORK}/joined.mp4"], check=True)

    async def speak():
        for i, seg in enumerate(SEG):
            await edge_tts.Communicate(seg[4], VOICE, rate=RATE).save(f"{WORK}/r{i}.mp3")
    asyncio.run(speak())
    for i in range(len(SEG)):
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", f"{WORK}/r{i}.mp3",
                        "-af", "silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-45dB",
                        "-y", f"{WORK}/n{i}.mp3"], check=True)

    t, starts, ok = 0.0, [], True
    for i, seg in enumerate(SEG):
        start = t + 0.3
        d = duration(f"{WORK}/n{i}.mp3")
        over = start + d > t + seg[3]
        ok &= not over
        starts.append(start)
        print(f"n{i}: {t:5.1f}-{t + seg[3]:5.1f}  voice {d:5.2f} ends {start + d:5.2f}  "
              f"{'OVERRUNS' if over else 'ok'}")
        t += seg[3]
    print(f"total {t:.1f}s | {'all fit' if ok else 'SHORTEN A CAPTION'}")
    if not ok:
        raise SystemExit(1)

    ins = ["-i", f"{WORK}/joined.mp4"]
    for i in range(len(SEG)):
        ins += ["-i", f"{WORK}/n{i}.mp3"]
    filt, labels = [], []
    for i, start in enumerate(starts):
        filt.append(f"[{i + 1}:a]adelay={int(start * 1000)}:all=1,aresample=48000[a{i}]")
        labels.append(f"[a{i}]")
    filt.append("".join(labels) + f"amix=inputs={len(SEG)}:normalize=0:dropout_transition=0,apad[aout]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-t", str(t), "-y", OUT], check=True)

    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", "3", "-i", OUT,
                    "-frames:v", "1", "-y", f"{WORK}/poster.png"], check=True)
    Image.open(f"{WORK}/poster.png").save(POSTER, "WEBP", quality=86, method=6)
    print(f"built {duration(OUT):.1f}s  {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
