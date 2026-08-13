# -*- coding: utf-8 -*-
"""Build the demos-page thumbnail for the virtual kiosk test.

Three screens rather than all eight: at the size a card actually renders, eight
panels are seventy pixels wide each and read as coloured slivers. Start, the
menu, and the keypad carry the whole shape of the task — arrive, choose, pay —
and stay legible.

    python tools/gen_kiosk_thumb.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(ROOT, "assets", "demos", "kiosk")
OUT = os.path.join(PANELS, "sequence.webp")

PICK = ["panel01", "panel03", "panel07"]   # arrive, choose, pay
GAP = 46                                   # gutter between screens
PAD = 46
BG = (245, 249, 249)                       # --soft, so it sits on the card
EDGE = (223, 231, 233)                     # --line


def main():
    shots = [Image.open(os.path.join(PANELS, p + ".webp")).convert("RGB") for p in PICK]
    w, h = shots[0].size
    canvas = Image.new("RGB", (PAD * 2 + w * len(shots) + GAP * (len(shots) - 1), PAD * 2 + h), BG)
    for i, shot in enumerate(shots):
        x = PAD + i * (w + GAP)
        # A hairline in the site's border colour, so each screen reads as a
        # screen rather than as a bleed of white into the card.
        canvas.paste(Image.new("RGB", (w + 2, h + 2), EDGE), (x - 1, PAD - 1))
        canvas.paste(shot, (x, PAD))
    canvas.thumbnail((1500, 1500), Image.LANCZOS)
    canvas.save(OUT, "WEBP", quality=88, method=6)
    print("%s  %s  %d bytes" % (OUT, canvas.size, os.path.getsize(OUT)))


main()
