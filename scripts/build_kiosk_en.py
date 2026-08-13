"""Generate the English text layer for the virtual kiosk demo.

The kiosk screens are the study's own panels, with Korean text baked into the
image. Rather than repaint them — which would destroy the originals and blur
the type — the demo lays real text over them. Each label is a chip filled with
the colour of the panel underneath it, so it covers the Korean seamlessly and
the English on top stays crisp at any size.

This script samples that colour from the source PNGs, so the chips match even
if the panels are ever re-exported.

Usage:  python scripts/build_kiosk_en.py [--check]
"""

import json
import os
import sys
from collections import Counter

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(ROOT, "assets", "demos", "kiosk")
OUT = os.path.join(ROOT, "assets", "demos", "kiosk-en.js")

# Each entry is a search window on the panel, not a measured box: the script
# finds the Korean inside it and fits the English chip to what it finds, so the
# labels stay aligned even if a panel is re-exported.
#   (x, y, w, h, english, align, run)   run 0 = first line of text in the window
L, C = "left", "center"
LAYERS = {
    "panel01": [(4, 24, 86, 17, "To start your order,|press the START button.", L, None),
                (28, 54, 44, 16, "START", C, 0)],
    "panel02": [(4, 24, 86, 17, "Where will you be|eating today?", L, None),
                (9, 65, 34, 9, "Eat in", C, 0),
                (56, 65, 34, 9, "Take out", C, 0)],
    "panel03": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 20, 97, 14, "Choose a BURGER.", L, 0),
                (1, 62, 97, 14, "Choose a SIDE.", L, 0),
                (1, 76, 97, 12, "Choose a DRINK.", L, 0)],
    "panel04": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 25.6, 80, 4.4, "Choose a BURGER.", L, None),
                (1, 39.2, 80, 4.4, "Choose a SIDE.", L, None),
                (1, 78, 97, 12, "Choose a DRINK.", L, 0)],
    "panel05": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 19, 70, 12, "Choose a BURGER.", L, 0),
                (1, 34, 70, 12, "Choose a SIDE.", L, 0),
                (1, 48, 97, 12, "Choose a DRINK.", L, 0)],
    "panel06": [(69, 3.0, 23, 3.4, "Back", C, None),
                (4, 18, 86, 12, "Check your order.", L, 0),
                (4, 43, 86, 12, "Choose how to pay.", L, 0),
                (9, 76, 34, 9, "Card", C, 0),
                (56, 76, 34, 9, "Mobile voucher", C, 0)],
    "panel07": [(69, 3.0, 23, 3.4, "Back", C, None),
                (7, 65.5, 15, 6.5, "DELETE", C, None),
                (71, 65, 21, 9, "OK", C, 0)],
    "panel08": [(10, 58, 80, 14, "Thank you.", C, 0)],
}

# Menu item names, in the four columns the demo already uses as click targets.
COLS = [(3.5, 24.2), (27.6, 48.3), (51.8, 72.4), (75.9, 96.5)]
GRIDS = {
    "panel03": [(40.0, 2.2, ["Beef Burger", "Cheese Burger", "Chicken Burger", "Garlic Burger"]),
                (54.0, 2.2, ["Bulgogi Burger", "Onion Burger", "Shrimp Burger", "Tomato Burger"])],
    "panel04": [(53.8, 2.2, ["Fries", "Cheese Sticks", "String Cheese", "Hash Brown"]),
                (67.7, 2.2, ["Chicken Wrap", "Apple Pie", "Hotcake", "Chicken Nuggets"])],
    "panel05": [(67.2, 2.2, ["Coca-Cola", "Cider", "Fanta Orange", "Water"]),
                (81.3, 2.2, ["Vanilla Shake", "Choco Shake", "Berry Shake", "Milk"])],
    # the confirmation screen repeats the three items in wider cards
    "panel06": [(39.4, 2.6, ["Shrimp Burger", "Cheese Sticks", "Coca-Cola"])],
}
CONFIRM_COLS = [(3.3, 29.0), (37.3, 63.0), (70.7, 96.3)]


def ink_for(hex_bg):
    """Text colour for a chip: the panel's bars are navy and red, its menus are
    white. Pick whichever of the two reads on the sampled background."""
    r, g, b = (int(hex_bg[i:i + 2], 16) for i in (1, 3, 5))
    return "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 150 else "#17252a"


def px(im, box):
    W, H = im.size
    x, y, w, h = box
    return (round(x / 100 * W), round(y / 100 * H),
            round((x + w) / 100 * W), round((y + h) / 100 * H))


def modal_colour(im, box):
    """The colour the chip must be: what the panel is behind this text.

    The mode, not the mean — text pixels are a minority, and averaging them in
    would tint the chip and leave a visible patch.
    """
    counts = Counter(im.crop(px(im, box)).getdata())
    return "#%02x%02x%02x" % counts.most_common(1)[0][0]


def fit(im, window, run):
    """Find the Korean inside `window` and return the box it occupies.

    Rows that differ from the window's background are text. Grouping them into
    runs separates a menu item's name from the price underneath it, so `run=0`
    takes the name and leaves the price showing.
    """
    W, H = im.size
    x0, y0, x1, y1 = px(im, window)
    crop = im.crop((x0, y0, x1, y1))
    bg = Counter(crop.getdata()).most_common(1)[0][0]
    cw, ch = crop.size
    pix = crop.load()

    def differs(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 90

    rows = [any(differs(pix[x, y]) for x in range(0, cw, 2)) for y in range(ch)]
    runs, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if y - start > ch * 0.04:            # ignore speckle
                runs.append((start, y))
            start = None
    if not runs:
        return None

    def extent(a, b):
        cols = [any(differs(pix[x, y]) for y in range(a, b)) for x in range(cw)]
        if not any(cols):
            return None
        return cols.index(True), cw - 1 - cols[::-1].index(True)

    if run is None:
        top, bottom = runs[0][0], runs[-1][1]
    else:
        # The widest line in the window is the one worth translating: it beats
        # the circled step number beside a heading, and the price under a menu
        # item. Lines that fill the window are borders and photo edges, not text.
        wide = [(extent(a, b), a, b) for a, b in runs]
        wide = [(g[1] - g[0], a, b) for g, a, b in wide if g]
        if not wide:
            return None
        # A line that fills the window is a border, not text — unless it is the
        # only thing there, in which case the label simply is that wide.
        scored = [s for s in wide if s[0] < cw * 0.97] or wide
        _, top, bottom = max(scored)

    got = extent(top, bottom)
    if not got:
        return None
    left, right = got

    pad_x, pad_y = round(cw * 0.02) + 2, round((bottom - top) * 0.06) + 1
    box = ((x0 + left - pad_x) / W * 100, (y0 + top - pad_y) / H * 100,
           (right - left + 2 * pad_x) / W * 100, (bottom - top + 2 * pad_y) / H * 100)
    return box


def label(im, window, text, align, run, aspect):
    box = fit(im, window, run)
    if box is None:
        return None
    x, y, w, h = box
    lines = text.split("|")
    # Height first, then shrink if the widest line would overflow the chip.
    size = h * aspect / len(lines) * 0.62
    widest = max(len(s) for s in lines)
    size = min(size, w / (0.52 * widest) * 0.96)
    bg = modal_colour(im, (x, y, w, h))
    return {"x": round(x, 2), "y": round(y, 2), "w": round(w, 2), "h": round(h, 2),
            "t": lines, "s": round(size, 2), "a": align, "bg": bg, "c": ink_for(bg)}


def build():
    layers = {}
    for panel in sorted(set(list(LAYERS) + list(GRIDS))):
        with Image.open(os.path.join(PANELS, panel + ".png")) as opened:
            im = opened.convert("RGB")
        aspect = im.height / im.width      # 1% of height is `aspect`% of width
        items = []
        for x, y, w, h, text, align, run in LAYERS.get(panel, []):
            got = label(im, (x, y, w, h), text, align, run, aspect)
            if got:
                items.append(got)
            else:
                print("  ! nothing found for %r on %s" % (text, panel))
        for row_y, row_h, names in GRIDS.get(panel, []):
            cols = CONFIRM_COLS if panel == "panel06" else COLS
            for (left, right), name in zip(cols, names):
                if name is None:
                    continue
                got = label(im, (left, row_y, right - left, row_h), name, C, None, aspect)
                if got:
                    items.append(got)
        layers[panel] = items
    return layers


def main():
    layers = build()
    nl = chr(10)
    header = ("/* Generated by scripts/build_kiosk_en.py - do not edit by hand.",
              "   English labels laid over the Korean panels, fitted to the text",
              "   they cover and filled with the colour sampled underneath. */")
    body = (nl.join(header) + nl + "window.KIOSK_EN = "
            + json.dumps(layers, indent=0, ensure_ascii=False) + ";" + nl)
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != body:
            sys.exit("kiosk-en.js is out of date — run python scripts/build_kiosk_en.py")
        print("kiosk-en.js up to date")
        return
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(body)
    print("wrote %s  (%d panels, %d labels)"
          % (os.path.relpath(OUT, ROOT), len(layers), sum(len(v) for v in layers.values())))


if __name__ == "__main__":
    main()
