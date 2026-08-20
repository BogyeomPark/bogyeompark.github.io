"""Build the career-agent demo video: the system running, then what it is for.

The picture is the prototype's own interface, animated in scripts/ca_animation.html
and recorded in a headless browser -- the same page the AIED workshop demo used,
with the student renamed and every claim about him rewritten in they/them.

What is new here is the timing. The earlier cut logged caption times off a
wall clock inside the page, then guessed a fixed offset back onto the recording
and delayed each narration clip by it; captions that ran to two lines and voice
lines that outlasted their caption did the rest, and the film drifted. Nothing
is guessed now:

  * The voice is generated first, and each beat is told to last at least as
    long as its own line -- so a caption can never be taken off screen while
    it is still being spoken. The page waits; the build does not trim.
  * Each beat paints a colour patch naming itself, inside the strip the caption
    bar covers, and the build reads the patch back out of the recording. The
    bar and the voice are placed on the frame the patch actually changes on,
    not on the frame a clock said it would.

Captions follow the kiosk film: one bar, 100px, 27px bold, and one line -- the
build fails rather than wrap, which is what forces the beats to stay short. The
ending is the kiosk's too: two cards for what the expert validation found, then
a coda with the bar empty and the line set large in the picture.

The closing cards carried the expert-validation scores for a while. They were
the strongest evidence in the paper and the wrong ending for this film: nothing
in the ninety seconds before them is about a number, and a scale appearing at
the end asks the viewer to judge the system rather than to see the split it is
built on. The scores are on /publications/agentic-career-hci2026/, where the
argument for them is.

Usage:
  python scripts/build_ca_video.py
"""

import asyncio
import functools
import glob
import http.server
import json
import os
import re
import socketserver
import subprocess
import threading

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "ca_animation.html"
SERVE = os.path.join(ROOT, "scripts")
WORK = os.path.join(ROOT, "tmp", "ca_build")
DEMO = os.path.join(ROOT, "assets", "demos", "career-agent")
OUT = os.path.join(DEMO, "system-demo.mp4")
POSTER = os.path.join(DEMO, "poster.webp")
THUMB = os.path.join(DEMO, "thumb.webp")

W, H, BAR_H = 1280, 720, 100
VID_H = H - BAR_H                # 620: the picture above the caption bar
FPS = 30
BAR_BG = (17, 27, 36)
VOICE, RATE = "en-US-AriaNeural", "-15%"   # same voice and pace as the other two
LEAD = 0.3                       # caption is up this long before the voice starts
TAIL_PAD = 0.55                  # quiet after a line before the beat may end
XFADE = 0.35
# Every segment but the last runs a second past its own end, for the dissolve
# to eat. It has to be comfortably more than XFADE, because xfade answers a
# transition that reaches past its first input by ending the film there rather
# than by failing -- which is silent, and cost two builds to find. For the
# recorded half that second is real: the page holds the finished report for a
# moment after the last beat, and those frames are better than cloned ones.
PAD = 1.0

# The marker patch: 48x36 at the bottom-left of the caption strip, sampled well
# inside its own edges so nothing the codec smears at the boundary is read.
MARK_CROP = (24, 20, 12, 692)    # w, h, x, y
MARK_G = 140                     # green channel above this means "in a beat"
MARK_R0, MARK_STEP = 16, 15      # beat i is red 16 + 15i; ca_animation.html paints it
MARK_STABLE = 4                  # frames a reading has to hold for to count

SB = r"C:\Windows\Fonts\seguisb.ttf"
BD = r"C:\Windows\Fonts\segoeuib.ttf"
f_cap = ImageFont.truetype(BD, 27)

# Site tokens. ACCENT is the rule under the coda, and it is the same navy the
# other two demo films rule their codas with.
INK, BODY, MUTED = (23, 37, 42), (70, 87, 92), (102, 120, 125)
PAPER_BG, SOFT, LINE = (255, 255, 255), (245, 249, 249), (223, 231, 233)
ACCENT = (31, 66, 117)

# One caption per beat. Beats 0-15 are the page; 16 is drawn here. A caption
# is one string, or (what the bar shows, what the voice says) -- the coda says
# its line in the picture, so its bar is empty.
BEATS = [
    "The teacher uploads the student's school records — all at once.",
    "Four files a teacher would otherwise read one by one.",
    "The agents read all four and draft the report.",
    "It comes back whole — summary, careers, electives, activities.",
    "Strengths and growth areas, each with a next step attached.",
    "Two career directions, inferred from the record itself.",
    "Electives chosen for the path, each with its reason.",
    "And activities to develop, area by area.",
    "Every claim in the report carries a reference number.",
    "Hover one, and the exact line from the record appears.",
    "Later, the teacher learns something no record held.",
    "A new interest, typed into the chat.",
    "The agent reconsiders, and proposes an update.",
    "One click applies it.",
    "The summary rewrites itself, and the subject note follows.",
    "The new lines came from the teacher, not the record.",
    ("", "Built from what teachers called costly, not from what a model can generate."),
]
PAGE_BEATS = 16                  # 0..15 come off the recording
CODA = ("Built from what teachers called costly,", "not from what a model can generate.")


def cap_parts(cap):
    """A caption is one string, or (what the bar shows, what the voice says)."""
    return cap if isinstance(cap, tuple) else (cap, cap)


def duration(path):
    # ffmpeg writes this to stderr and exits non-zero when given no output file;
    # decode defensively because the console codepage here is not UTF-8.
    res = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    out = (res.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        raise SystemExit("no duration for " + path + ":\n" + out[-400:])
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


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


def caption_bar(text, path):
    im = Image.new("RGBA", (W, BAR_H), BAR_BG + (255,))
    d = ImageDraw.Draw(im)
    if not text:
        im.save(path)
        return
    # one line, always: a second line halves the picture's breathing room, and
    # two short beats read better than one long caption over a long shot
    lines = wrap(d, text, f_cap, W - 140)
    if len(lines) > 1:
        raise SystemExit(f"caption needs {len(lines)} lines: {text}")
    d.text(((W - d.textlength(text, font=f_cap)) / 2, (BAR_H - 34) // 2), text,
           font=f_cap, fill=(255, 255, 255, 255))
    im.save(path)


def ease(x):
    """Ease-out cubic, clamped."""
    x = 0.0 if x < 0 else (1.0 if x > 1 else x)
    return 1 - (1 - x) ** 3


def draw_coda(t):
    """The line the rest of it has been walking towards."""
    im = Image.new("RGB", (W, VID_H), PAPER_BG)
    f_big = ImageFont.truetype(BD, 46)
    p = ease(t / 0.8)
    y = 258 + int((1 - p) * 16)
    layer = Image.new("RGB", (W, 160), PAPER_BG)
    ld = ImageDraw.Draw(layer)
    ld.rectangle([(W - 96) // 2, 0, (W + 96) // 2, 5], fill=ACCENT)
    for n, line in enumerate(CODA):
        ld.text(((W - ld.textlength(line, font=f_big)) / 2, 44 + n * 58), line,
                font=f_big, fill=INK if n == 0 else BODY)
    im.paste(Image.blend(Image.new("RGB", (W, 160), PAPER_BG), layer, p), (0, y - 44))
    return im


def render_drawn(frame, dur, path):
    """Render a drawn beat frame by frame and pipe it straight into ffmpeg."""
    proc = subprocess.Popen(
        [FF, "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{VID_H}", "-framerate", str(FPS), "-i", "-",
         "-vf", f"pad={W}:{H}:0:0:color=0x111b24", "-c:v", "libx264", "-crf", "20",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-y", path],
        stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        proc.stdin.write(frame(i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed on " + path)


def speak(lines):
    """One mp3 per spoken line, trimmed of the silence the voice pads with."""
    async def gen():
        for i, line in lines:
            await edge_tts.Communicate(line, VOICE, rate=RATE).save(f"{WORK}/r{i}.mp3")
    asyncio.run(gen())
    out = {}
    for i, _ in lines:
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", f"{WORK}/r{i}.mp3",
                        "-af", "silenceremove=stop_periods=-1:stop_duration=0.12:"
                               "stop_threshold=-45dB",
                        "-y", f"{WORK}/n{i}.mp3"], check=True)
        out[i] = duration(f"{WORK}/n{i}.mp3")
    return out


def record(holds):
    """Play the page once with those beat lengths, and keep the recording."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SERVE)

    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    httpd = Quiet(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    from playwright.sync_api import sync_playwright
    vid = os.path.join(WORK, "vid")
    os.makedirs(vid, exist_ok=True)
    for f in glob.glob(os.path.join(vid, "*.webm")):
        os.remove(f)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True, args=[
                "--autoplay-policy=no-user-gesture-required", "--hide-scrollbars",
                "--force-device-scale-factor=1"])
            ctx = browser.new_context(viewport={"width": W, "height": H},
                                      device_scale_factor=1, record_video_dir=vid,
                                      record_video_size={"width": W, "height": H})
            page = ctx.new_page()
            page.add_init_script(f"window.__HOLD = {json.dumps(holds)};")
            page.goto(f"http://127.0.0.1:{port}/{PAGE}", wait_until="load")
            page.wait_for_function("window.__done === true",
                                   timeout=int((sum(holds) + 60) * 1000))
            marks = page.evaluate("window.__T")
            # keep rolling on the finished report: those frames are the tail
            # the dissolve into the closing cards is cut from
            page.wait_for_timeout(1500)
            page.close()
            ctx.close()
            browser.close()
    finally:
        httpd.shutdown()
    return max(glob.glob(os.path.join(vid, "*.webm")), key=os.path.getmtime), marks


def read_marks(path):
    """Beat -> first frame it is painted on, read back out of the recording.

    Reading it is not just a matter of looking at one frame. The patch changes
    colour between two frames and the recorder can catch one part-way through;
    worse, the codec drops the odd block of a neighbouring beat's colour into
    the middle of a beat, once for a single frame and once for two in a row. So
    a reading only counts when it is the next beat in the sequence and holds for
    four frames together -- beats run in order, none is revisited, and none is
    anywhere near four frames long, which is enough to throw every artefact out.

    The end of the run is read the same way: four frames of the black the page
    paints once the last beat is over. An unreadable frame is not an ending --
    that is what an artefact looks like too.
    """
    w, h, x, y = MARK_CROP
    res = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", path,
                          "-vf", f"crop={w}:{h}:{x}:{y},scale=1:1:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True)
    px = res.stdout
    n = len(px) // 3

    def read(f):
        if not 0 <= f < n:
            return None
        r, g = px[f * 3], px[f * 3 + 1]
        if g < MARK_G:
            return None
        i = round((r - MARK_R0) / MARK_STEP)
        if 0 <= i < PAGE_BEATS and abs(r - (MARK_R0 + i * MARK_STEP)) <= 5:
            return i
        return None

    def dark(f):
        return all(0 <= f + k < n and px[(f + k) * 3 + 1] < MARK_G
                   for k in range(MARK_STABLE))

    frames, last, end = {}, -1, None
    for f in range(n):
        if last >= 0 and dark(f):
            end = f
            break
        i = read(f)
        if i == last + 1 and all(read(f + k) == i for k in range(MARK_STABLE)):
            frames[i], last = f, i
    missing = [i for i in range(PAGE_BEATS) if i not in frames]
    if missing:
        raise SystemExit(f"beats not found in the recording: {missing}")
    if end is None:
        raise SystemExit("the recording never reaches the end of the last beat")
    return [frames[i] for i in range(PAGE_BEATS)], end, n


def main():
    os.chdir(ROOT)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(DEMO, exist_ok=True)
    for f in glob.glob(os.path.join(WORK, "*.mp4")) + glob.glob(os.path.join(WORK, "*.png")):
        os.remove(f)

    # 1. the bars first: a caption that will not fit on one line stops the
    #    build here, before an hour of voice and recording is spent on it
    for i, c in enumerate(BEATS):
        caption_bar(cap_parts(c)[0], f"{WORK}/c{i}.png")
    voiced = [(i, cap_parts(c)[1]) for i, c in enumerate(BEATS) if cap_parts(c)[1]]
    vdur = speak(voiced)
    need = [LEAD + vdur.get(i, 0.0) + TAIL_PAD for i in range(len(BEATS))]

    # 2. record the page, then find each beat in the recording rather than
    #    trusting the clock the page kept while it played
    webm, page_marks = record([round(x, 3) for x in need[:PAGE_BEATS]])
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", webm,
                    "-vf", f"scale={W}:{H},setsar=1", "-r", str(FPS), "-an",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-y", f"{WORK}/raw.mp4"], check=True)
    starts, end_f, shot = read_marks(f"{WORK}/raw.mp4")
    t0 = starts[0]
    body = [(f - t0) / FPS for f in starts]
    body_len = (end_f - t0) / FPS
    for i, (clock, seen) in enumerate(zip([m["t"] for m in page_marks if m["i"] >= 0], body)):
        drift = seen - (clock - page_marks[0]["t"])
        print(f"beat {i:2d}  page {clock - page_marks[0]['t']:6.2f}s  "
              f"recorded {seen:6.2f}s  drift {drift:+.2f}s")

    # 3. the one drawn beat at the end. The two conclusion cards that used to
    # sit here restated what the recording had just shown, and held still for
    # over four seconds each doing it, so the film ended twice
    render_drawn(draw_coda, need[16] + PAD, f"{WORK}/coda.mp4")
    body_last = min(shot, end_f + int(round(PAD * FPS)))
    if (body_last - end_f) / FPS < XFADE + 0.1:
        raise SystemExit(f"only {(body_last - end_f) / FPS:.2f}s of recording past the "
                         f"last beat; the dissolve into the coda needs {XFADE}s")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", f"{WORK}/raw.mp4",
                    "-vf", f"trim=start_frame={t0}:end_frame={body_last},setpts=PTS-STARTPTS",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), "-y", f"{WORK}/body.mp4"], check=True)

    seg_start = [0.0, body_len]
    total = body_len + need[16]
    starts_at = body + [body_len]
    ends_at = starts_at[1:] + [total]

    # 4. join the two pieces, then burn one caption bar per beat on the join
    ins = ["-i", f"{WORK}/body.mp4", "-i", f"{WORK}/coda.mp4"]
    for i in range(len(BEATS)):
        ins += ["-i", f"{WORK}/c{i}.png"]
    chain, last = [], "0:v"
    for n in (1,):
        chain.append(f"[{last}][{n}:v]xfade=transition=fadewhite:duration={XFADE}:"
                     f"offset={seg_start[n]:.3f}[x{n}]")
        last = f"x{n}"
    for i in range(len(BEATS)):
        chain.append(f"[{last}][{2 + i}:v]overlay=0:H-{BAR_H}:"
                     f"enable='between(t,{starts_at[i]:.3f},{ends_at[i]:.3f})'[k{i}]")
        last = f"k{i}"
    chain.append(f"[{last}]fade=t=out:st={total - 0.9:.2f}:d=0.9:color=white[out]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins,
                    "-filter_complex", ";".join(chain), "-map", "[out]",
                    "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), "-t", str(total), "-y",
                    f"{WORK}/captioned.mp4"], check=True)
    made = duration(f"{WORK}/captioned.mp4")
    if made < total - 0.1:
        raise SystemExit(f"the join came out {made:.2f}s, not {total:.2f}s: a "
                         f"segment ran out under its own dissolve")

    # 5. the voice, on the beat the bar went up on
    ok = True
    for i, _ in voiced:
        over = starts_at[i] + LEAD + vdur[i] > ends_at[i] + 0.01
        ok &= not over
        print(f"n{i:2d}: {starts_at[i]:5.1f}-{ends_at[i]:5.1f}  voice {vdur[i]:5.2f}  "
              f"ends {starts_at[i] + LEAD + vdur[i]:5.2f}  {'OVERRUNS' if over else 'ok'}")
    print(f"total {total:.1f}s | {'all fit' if ok else 'A BEAT IS TOO SHORT'}")
    if not ok:
        raise SystemExit(1)

    ins = ["-i", f"{WORK}/captioned.mp4"]
    for i, _ in voiced:
        ins += ["-i", f"{WORK}/n{i}.mp3"]
    filt, labels = [], []
    for n, (i, _) in enumerate(voiced):
        filt.append(f"[{n + 1}:a]adelay={int((starts_at[i] + LEAD) * 1000)}:all=1,"
                    f"aresample=48000[a{n}]")
        labels.append(f"[a{n}]")
    filt.append("".join(labels) + f"amix=inputs={len(voiced)}:normalize=0:"
                                  f"dropout_transition=0,apad[aout]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", *ins,
                    "-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-t", str(total), "-y", OUT], check=True)

    at = starts_at[9] + 1.6      # the source of a claim, open on screen
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", f"{at:.2f}",
                    "-i", OUT, "-frames:v", "1", "-y", f"{WORK}/poster.png"], check=True)
    poster = Image.open(f"{WORK}/poster.png")
    poster.save(POSTER, "WEBP", quality=86, method=6)
    poster.resize((1024, 576), Image.LANCZOS).save(THUMB, "WEBP", quality=86, method=6)
    print(f"built {duration(OUT):.1f}s  {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
