"""Build the kiosk demo's screens and its English text layer.

The screens are the study's own panels, with Korean baked into the pixels. The
demo used to lay opaque chips over that Korean at runtime, which had two costs:
the Korean was visible for as long as the label layer took to fade in, and every
chip had to hug the glyphs it covered — the old code carried notes about shaving
a card's corner and grazing a circled number.

This script does the covering once, in the image:

  1. it measures where the Korean is, exactly as the chips used to;
  2. it erases each box by growing it out to the flat colour around it, which
     stops on its own at a band's edge, a photo or a circled number;
  3. it blanks the six cards that show a fixed order (shrimp burger, cheese
     sticks, Coca-Cola) so the demo can draw what was actually chosen;
  4. it writes panelNN-en.webp and the geometry the demo needs to draw on them.

The originals — panelNN.png — are never written to. Re-run this after any
re-export of them.

Usage:  python scripts/build_kiosk_panels.py [--out DIR] [--check]
"""

import json
import os
import sys
from collections import Counter

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(ROOT, "assets", "demos", "kiosk")
OUT_JS = os.path.join(ROOT, "assets", "demos", "kiosk-en.js")

L, C = "left", "center"

# --- text to cover -------------------------------------------------------
# Each entry is a search window, not a measured box: the script finds the Korean
# inside it and fits the English to what it finds.
#   (x, y, w, h, english, align, run[, radius[, span]])
#   run 0 = the widest line of text in the window; radius (cqw) rounds a chip
#   that covers a whole control; span = (x, w) widens it past the fitted Korean.
LAYERS = {
    "panel01": [(4, 24, 86, 17, "To start your order,|press the START button.", L, None),
                (28, 54, 44, 16, "START", C, 0)],
    "panel02": [(4, 24, 86, 17, "Where will you be|eating today?", L, None),
                (5, 65, 42, 9, "Eat in", C, 0),
                (53.5, 65, 42, 9, "Take out", C, 0)],
    "panel03": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 20, 97, 14, "Choose a BURGER.", L, 0),
                (1, 62, 97, 14, "Choose a SIDE.", L, 0),
                (1, 76, 97, 12, "Choose a DRINK.", L, 0)],
    "panel04": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 25.6, 78.1, 4.4, "Choose a BURGER.", L, None),
                (1, 39.2, 78.1, 4.4, "Choose a SIDE.", L, None),
                (1, 78, 97, 12, "Choose a DRINK.", L, 0)],
    "panel05": [(69, 3.0, 23, 3.4, "Back", C, None),
                (1, 25.6, 78.1, 4.4, "Choose a BURGER.", L, None),
                (1, 39.2, 78.1, 4.4, "Choose a SIDE.", L, None),
                (1, 48, 97, 12, "Choose a DRINK.", L, 0)],
    "panel06": [(69, 3.0, 23, 3.4, "Back", C, None),
                (4, 18, 86, 12, "Check your order.", L, 0),
                (4, 43, 86, 12, "Choose how to pay.", L, 0),
                (9, 76, 34, 9, "Card", C, 0),
                (52.5, 76, 42.5, 9, "Mobile voucher", C, 0)],
    "panel07": [(69, 3.0, 23, 3.4, "Back", C, None),
                (7.5, 64.5, 23, 10.5, "DELETE", C, None, 4.6),
                (71, 65, 21, 9, "OK", C, 0)],
    "panel08": [(10, 58, 80, 14, "Thank you.", C, 0)],
}

# --- the menu itself -----------------------------------------------------
# Korean name (the demo's own click-target labels), English name, and the price
# printed on the tile. Row-major: four columns, two rows, as they appear.
ITEMS = {
    "panel03": [("소고기버거", "Beef Burger", "3,200원"),
                ("치즈버거", "Cheese Burger", "6,000원"),
                ("치킨버거", "Chicken Burger", "5,200원"),
                ("마늘버거", "Garlic Burger", "3,200원"),
                ("불고기버거", "Bulgogi Burger", "3,200원"),
                ("양파버거", "Onion Burger", "3,200원"),
                ("새우버거", "Shrimp Burger", "5,200원"),
                ("토마토버거", "Tomato Burger", "5,100원")],
    "panel04": [("감자튀김", "Fries", "+0원"),
                ("치즈스틱", "Cheese Sticks", "+500원"),
                ("스트링 치즈", "String Cheese", "+1,200원"),
                ("해시브라운", "Hash Brown", "+1,500원"),
                ("치킨 랩", "Chicken Wrap", "+1,500원"),
                ("사과 파이", "Apple Pie", "+1,700원"),
                ("핫케이크", "Hotcake", "+2,200원"),
                ("치킨 너겟", "Chicken Nuggets", "+4,500원")],
    "panel05": [("코카콜라", "Coca-Cola", "+500원"),
                ("사이다", "Cider", "+500원"),
                ("환타 오렌지", "Fanta Orange", "+0원"),
                ("생수", "Water", "+500원"),
                ("바닐라 쉐이크", "Vanilla Shake", "+1,200원"),
                ("초코 쉐이크", "Choco Shake", "+1,200원"),
                ("딸기 쉐이크", "Berry Shake", "+1,700원"),
                ("우유", "Milk", "+500원")],
}
# the four columns the demo already uses as click targets
COLS = [(3.5, 24.2), (27.6, 48.3), (51.8, 72.4), (75.9, 96.5)]
# search windows for the two rows of tiles, and for the name line inside them
TILE_ROWS = {"panel03": [(32.6, 43.5), (46.5, 57.5)],
             "panel04": [(46.3, 57.2), (60.3, 71.2)],
             "panel05": [(59.7, 70.8), (73.9, 84.7)]}
NAME_ROWS = {"panel03": [(40.0, 1.75), (54.0, 1.75)],
             "panel04": [(53.8, 1.75), (67.7, 1.8)],
             "panel05": [(67.15, 1.8), (81.3, 1.7)]}

# --- the cards that carry a fixed order ---------------------------------
# Search windows for the baked-in chosen-item cards. Each becomes an empty card
# that the demo fills in with whatever was actually chosen.
SLOTS = {
    "panel04": [("burger", (74, 13, 99.9, 31))],
    "panel05": [("burger", (74, 13, 99.9, 31)), ("side", (74, 30, 99.9, 46))],
    "panel06": [("burger", (1, 26, 33, 47)), ("side", (34, 26, 67, 47)),
                ("drink", (67, 26, 99.9, 47))],
}
SLOT_SOURCE = {"burger": "panel03", "side": "panel04", "drink": "panel05"}
# Labels that sit on the same row of the same control, and so must share a line
# and a size: fitted one at a time they land a few tenths of a percent apart,
# which reads as one of the pair sitting lower than the other.
LABEL_ROWS = {
    "panel02": [("Eat in", "Take out")],
    "panel06": [("Card", "Mobile voucher")],
    "panel07": [("DELETE", "OK")],
}
# The Back pill drifts between screens — 60.99% across on the confirmation and
# keypad screens, 63.49% on the collapsed headers, and three other values in
# between — while its size and its height never change. One hit box cannot follow
# five positions, so the pill is moved to the middle one of them and every screen
# gets it in the same place. BACK_BOX is that position, and kiosk.js uses it as
# its own Back target.
BACK_WINDOW = (50, 0.4, 49.5, 8.6)      # x, y, w, h — like every other window here
BACK_BOX = (62.89, 2.71, 33.2, 4.16)
# Two controls drawn side by side but not level with each other: on the payment
# screen the voucher card sits nine pixels above the card card. Same reasoning as
# the pill — the second one is moved onto the first one's line so that one
# measurement describes both.
ALIGN_PAIRS = {"panel06": [((1, 54, 48, 36), (50, 54, 49, 36))]}
WHITE = 249          # a card pixel; every panel grey sits below this
GROW_CAP = 0.03      # how far an erase may grow past the text, as a fraction


def find_pill(im, window=BACK_WINDOW):
    """The Back pill: the one dark shape in the top right of a screen."""
    x0, y0, x1, y1 = px(im, window)
    pix = im.load()
    bg = around_colour(im, (x0, y0, x1, y1), pad=2)
    dark = lambda p: sum(abs(a - b) for a, b in zip(p, bg)) > 60
    xs = [x for x in range(x0, x1) if sum(1 for y in range(y0, y1, 2) if dark(pix[x, y])) > 3]
    ys = [y for y in range(y0, y1) if sum(1 for x in range(x0, x1, 2) if dark(pix[x, y])) > 3]
    if not xs or not ys:
        return None
    return (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)


def find_control(im, window):
    """The bounding box of the one control inside `window`."""
    x0, y0, x1, y1 = px(im, window)
    pix = im.load()
    bg = around_colour(im, (x0, y0, x1, y1), pad=2)
    off = lambda p: sum(abs(a - b) for a, b in zip(p, bg)) > 26
    xs = [x for x in range(x0, x1) if sum(1 for y in range(y0, y1, 3) if off(pix[x, y])) > 2]
    ys = [y for y in range(y0, y1) if sum(1 for x in range(x0, x1, 3) if off(pix[x, y])) > 2]
    if not xs or not ys:
        return None
    return (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)


def shift_control(im, found, dx, dy, pad=10, wipe=22):
    """Move a control, taking its shadow with it and leaving the panel behind.

    Two margins, not one. `pad` is how much is carried along, enough to bring the
    control's soft shadow with it. `wipe` is how much is cleared, and has to be
    larger: the shadow fades out well past the box the control is found in, so a
    wipe the size of the cut left the outermost ring of the old shadow behind and
    the control read as double-outlined at its new position.
    """
    W, H = im.size
    cut = (max(0, found[0] - pad), max(0, found[1] - pad),
           min(W, found[2] + pad), min(H, found[3] + pad))
    piece = im.crop(cut)
    bg = around_colour(im, found, pad=wipe + 6)
    clear = (max(0, found[0] - wipe), max(0, found[1] - wipe),
             min(W, found[2] + wipe), min(H, found[3] + wipe))
    ImageDraw.Draw(im).rectangle([clear[0], clear[1], clear[2] - 1, clear[3] - 1],
                                 fill=tuple(bg[:3]))
    im.paste(piece, (cut[0] + dx, cut[1] + dy))


def align_pairs(im, panel):
    """Bring the second of a pair onto the first one's line."""
    for ref_win, move_win in ALIGN_PAIRS.get(panel, []):
        ref, mover = find_control(im, ref_win), find_control(im, move_win)
        if not ref or not mover or abs(ref[1] - mover[1]) < 2:
            continue
        shift_control(im, mover, 0, ref[1] - mover[1])
        print("     paired control moved %+d px to match its neighbour" % (ref[1] - mover[1]))


def unify_back(im, panel):
    """Move the Back pill to the one position every screen will share."""
    found = find_pill(im)
    if not found:
        return None
    target = px(im, BACK_BOX)
    dx, dy = target[0] - found[0], target[1] - found[1]
    if abs(dx) < 2 and abs(dy) < 2:
        return found
    shift_control(im, found, dx, dy)
    print("     back pill moved %+d px" % dx)
    return (found[0] + dx, found[1] + dy, found[2] + dx, found[3] + dy)


def trim_frame(im):
    """Drop the black strip down the left of some panels.

    panel03, 04 and 05 were exported three or four pixels wider than the rest,
    and the extra is a black edge left over from whatever captured them. The
    encoder used for the previous panels happened to smear it to white, so nobody
    saw it; encoded faithfully it is a black line down the side of the screen.
    Cutting it also makes all eight the same 1238 wide, which is the ratio the
    stylesheet holds the frame at.
    """
    px = im.load()
    ys = range(0, im.height, 7)
    black = lambda x: sum(1 for y in ys if sum(px[x, y]) < 40) > len(ys) * 0.9
    cut = 0
    while cut < 8 and black(cut):
        cut += 1
    return im.crop((cut, 0, im.width, im.height)) if cut else im


# ========================================================================
# measuring
# ========================================================================

def px(im, box):
    W, H = im.size
    x, y, w, h = box
    return (round(x / 100 * W), round(y / 100 * H),
            round((x + w) / 100 * W), round((y + h) / 100 * H))


def as_pct(im, box):
    W, H = im.size
    return (round(box[0] / W * 100, 2), round(box[1] / H * 100, 2),
            round((box[2] - box[0]) / W * 100, 2), round((box[3] - box[1]) / H * 100, 2))


def ink_for(hex_bg):
    """Text colour for a label: the panel's bars are navy and red, its menus are
    white. Pick whichever of the two reads on the sampled background."""
    r, g, b = (int(hex_bg[i:i + 2], 16) for i in (1, 3, 5))
    return "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 150 else "#17252a"


def modal_colour(im, box_px):
    """What the panel is behind this text: the mode, not the mean — text pixels
    are a minority and averaging them in would tint the fill."""
    counts = Counter(im.crop(box_px).getdata())
    return counts.most_common(1)[0][0]


def around_colour(im, box, pad=6):
    """The colour surrounding a text box: the mode of a frame just outside it.

    Sampling inside the box instead can return the ink. A short, bold name — 생수,
    two glyphs — fills its own fitted box more than the card behind it does, and
    the fill then paints the name's own black over the tile.
    """
    x0, y0, x1, y1 = box
    ox0, oy0 = max(0, x0 - pad), max(0, y0 - pad)
    ox1, oy1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    strips = [(ox0, oy0, ox1, y0), (ox0, y1, ox1, oy1),
              (ox0, y0, x0, y1), (x1, y0, ox1, y1)]
    counts = Counter()
    for s in strips:
        if s[2] > s[0] and s[3] > s[1]:
            counts.update(im.crop(s).getdata())
    if not counts:
        return modal_colour(im, box)
    return counts.most_common(1)[0][0]


def glyph_colour(im, box_px, bg):
    """The colour the Korean is drawn in, so the English replacing it matches.

    The mode of everything that is not the background: the glyphs' own body
    outnumbers their antialiased edges. Taken this way rather than as the darkest
    ink, which would read a white label on a navy band as the dark edge of its
    own strokes. Returns None if the box holds no text.
    """
    near = lambda p: sum(abs(a - b) for a, b in zip(p, bg)) <= 40
    ink = Counter(p for p in im.crop(box_px).getdata() if not near(p))
    if not ink:
        return None
    return "#%02x%02x%02x" % ink.most_common(1)[0][0]


def fit(im, window, run):
    """Find the Korean inside `window` and return the box it occupies."""
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
        wide = [(extent(a, b), a, b) for a, b in runs]
        wide = [(g[1] - g[0], a, b) for g, a, b in wide if g]
        if not wide:
            return None
        scored = [s for s in wide if s[0] < cw * 0.97] or wide
        _, top, bottom = max(scored)

    got = extent(top, bottom)
    if not got:
        return None
    left, right = got
    pad_x, pad_y = round(cw * 0.02) + 2, round((bottom - top) * 0.06) + 1
    return (max(x0, x0 + left - pad_x), max(y0, y0 + top - pad_y),
            min(x1, x0 + right + pad_x), min(y1, y0 + bottom + pad_y))


def grow_flat(im, box, bg, cap=GROW_CAP, tol=12):
    """Grow a text box out to the flat colour that surrounds it.

    A chip had to hug its Korean, because anything it overreached onto — a card's
    rounded corner, a circled step number — showed the overreach. An erase can be
    greedy instead: each edge advances only while the row or column it would
    swallow is uniformly the background, so it reaches the edge of the flat area
    and stops there by itself. The cap keeps a wide-open background (the thank-you
    screen) from growing the box across half the panel for nothing.
    """
    W, H = im.size
    pix = im.load()
    x0, y0, x1, y1 = box
    lim_x, lim_y = round(W * cap), round(H * cap)
    near = lambda p: sum(abs(a - b) for a, b in zip(p, bg)) <= tol

    def row_flat(y, a, b):
        return all(near(pix[x, y]) for x in range(a, b, 2))

    def col_flat(x, a, b):
        return all(near(pix[x, y]) for y in range(a, b, 2))

    for _ in range(lim_y):
        if y0 - 1 < 0 or not row_flat(y0 - 1, x0, x1):
            break
        y0 -= 1
    for _ in range(lim_y):
        if y1 + 1 >= H or not row_flat(y1, x0, x1):
            break
        y1 += 1
    for _ in range(lim_x):
        if x0 - 1 < 0 or not col_flat(x0 - 1, y0, y1):
            break
        x0 -= 1
    for _ in range(lim_x):
        if x1 + 1 >= W or not col_flat(x1, y0, y1):
            break
        x1 += 1
    return (x0, y0, x1, y1)


def white_blob(im, window):
    """Bounding box of the largest white blob in `window` — a card's name/price
    strip, which is the one part of it guaranteed to be flat white."""
    x0, y0, x1, y1 = px(im, (window[0], window[1], window[2] - window[0], window[3] - window[1]))
    crop = im.crop((x0, y0, x1, y1))
    pix = crop.load()
    cw, ch = crop.size
    seen = bytearray(cw * ch)
    best = None
    for sy in range(ch):
        for sx in range(cw):
            if seen[sy * cw + sx] or min(pix[sx, sy]) < WHITE:
                continue
            stack = [(sx, sy)]
            seen[sy * cw + sx] = 1
            n, bx0, bx1, by0, by1 = 0, sx, sx, sy, sy
            while stack:
                x, y = stack.pop()
                n += 1
                bx0, bx1 = min(bx0, x), max(bx1, x)
                by0, by1 = min(by0, y), max(by1, y)
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < cw and 0 <= ny < ch and not seen[ny * cw + nx] \
                            and min(pix[nx, ny]) >= WHITE:
                        seen[ny * cw + nx] = 1
                        stack.append((nx, ny))
            if best is None or n > best[0]:
                best = (n, bx0, by0, bx1, by1)
    if not best:
        return None
    _, bx0, by0, bx1, by1 = best
    return (x0 + bx0, y0 + by0, x0 + bx1 + 1, y0 + by1 + 1)


def ring_colour(im, window):
    """The panel behind a card: the modal colour of the search window's own
    border ring, which lies outside the card on every side."""
    x0, y0, x1, y1 = px(im, (window[0], window[1], window[2] - window[0], window[3] - window[1]))
    pix = im.load()
    ring = []
    for x in range(x0, x1):
        ring.append(pix[x, y0])
        ring.append(pix[x, y1 - 1])
    for y in range(y0, y1):
        ring.append(pix[x0, y])
        ring.append(pix[x1 - 1, y])
    return Counter(ring).most_common(1)[0][0]


def strip_runs(im, strip, ink=28, inset=None):
    """The lines of text inside a card's white strip.

    `inset` is the card's corner radius: the strip's own bottom rows are only
    white in the middle, because the corners have curved away into the band
    behind. Without that inset a collapsed header's price line ran into the red
    underneath it and read as one line half again as tall.
    """
    x0, y0, x1, y1 = strip
    pad = inset if inset is not None else max(2, round((x1 - x0) * 0.05))
    crop = im.crop((x0 + pad, y0, x1 - pad, y1))
    pix = crop.load()
    cw, ch = crop.size
    rows = []
    for y in range(ch):
        n = sum(1 for x in range(0, cw, 2) if 255 - min(pix[x, y]) > ink)
        rows.append(n > cw * 0.03)
    out, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if y - start >= 3:
                out.append((y0 + start, y0 + y))
            start = None

    # The card's own bottom edge and drop shadow are ink too. They are told apart
    # from the price line by width, not by height: an edge runs the full width of
    # the card, and no line of text does. Height alone mistook the thicker
    # shadow under a collapsed header's card for the price.
    def full_width(run):
        band = crop.crop((0, run[0] - y0, cw, run[1] - y0))
        cols = [any(255 - min(band.getpixel((x, y))) > ink for y in range(band.height))
                for x in range(cw)]
        return sum(cols) >= cw * 0.95

    return [r for r in out if not full_width(r)]


def card_of(im, window):
    """A card, as photo (flush to its top and sides) over a white strip.

    The card's top is found by walking up from the strip and comparing each row
    inside the card against the panel just beside it, at that same row. Comparing
    against one sampled background instead would walk straight up through a
    collapsed header's navy and stop above the band.

    Returns the card box, the strip box, and the two text lines in the strip.
    """
    strip = white_blob(im, window)
    if not strip:
        return None
    pix = im.load()
    xs = list(range(strip[0] + 3, strip[2] - 3, 2))
    left = max(0, strip[0] - 6)
    right = min(im.width - 1, strip[2] + 5)
    top = strip[1]
    while top > 0:
        y = top - 1
        beside = pix[left, y] if strip[0] >= 6 else pix[right, y]
        off = sum(1 for x in xs
                  if sum(abs(a - b) for a, b in zip(pix[x, y], beside)) > 14)
        if off < len(xs) * 0.5:
            break
        top -= 1
    card = (strip[0], top, strip[2], strip[3])
    radius = corner_radius(im, card)
    runs = strip_runs(im, strip, inset=radius + 2)
    if len(runs) < 2:
        return None
    # The name and the price are the two tallest runs in the strip: a line of
    # text stands two to four times as tall as the card's bottom edge, which is
    # the only other ink down here. Taking the last two runs instead read that
    # edge as the price and the price as the name, and no threshold on the edge's
    # own thickness held across both the wide cards and the collapsed headers.
    name, price = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:2])
    return {"card": card, "strip": strip, "r": radius,
            "name": name, "price": price, "bg": ring_colour(im, window)}


def corner_radius(im, card):
    """The corner radius, measured at the card's bottom edge.

    Measured there and not at the top because the bottom of a card is its white
    strip against a navy, red or grey band: the widest contrast on the panel, so
    the corner is unambiguous. A rounded corner reaches the card's full width r
    rows in from the edge, so the first row that spans the whole card gives r.
    """
    pix = im.load()
    x0, y0, x1, y1 = card
    w = x1 - x0
    for dy in range(1, min(round(w * 0.30), (y1 - y0) // 2)):
        xs = [x for x in range(x0, x1) if min(pix[x, y1 - 1 - dy]) >= WHITE]
        if xs and (xs[-1] - xs[0] + 1) >= w - 2:
            return max(2, dy)
    return round(w * 0.07)


# ========================================================================
# building
# ========================================================================

def erase_card(im, card, bg):
    """Take a card out of the panel, leaving the band it sat on.

    Earlier this kept the card and only emptied it, which meant the demo had to
    draw its content into a shape it could not see: the photo's square corners
    then hung over the card's rounded ones. Removing the card outright lets the
    demo draw the whole thing — white, radius, shadow and photo, one clipped box —
    so nothing can be a pixel out. It also leaves these screens honest when
    nothing has been chosen yet.
    """
    x0, y0, x1, y1 = grow_flat(im, card, bg, cap=0.06)
    ImageDraw.Draw(im).rectangle([x0, y0, x1 - 1, y1 - 1], fill=tuple(bg[:3]))


def label(im, box, text, align, aspect, span=None, radius=None):
    """An English label: where it goes, how big, and in what colour."""
    x, y, w, h = as_pct(im, box)
    if span:
        x, w = span
    lines = text.split("|")
    size = h * aspect / len(lines) * 0.62
    widest = max(len(s) for s in lines)
    per_char = 0.62 if text.replace("|", " ").isupper() else 0.52
    size = min(size, w / (per_char * widest) * 0.96)
    bg = around_colour(im, box)
    # The English inherits the colour the Korean was drawn in, so a navy label on
    # a white card stays navy rather than going to the generic ink.
    hex_bg = "#%02x%02x%02x" % bg
    out = {"x": round(x, 2), "y": round(y, 2), "w": round(w, 2), "h": round(h, 2),
           "t": lines, "s": round(size, 2), "a": align,
           "c": glyph_colour(im, box, bg) or ink_for(hex_bg)}
    if radius:
        out["r"] = radius
    return out


def build_panel(panel, im, tile_type):
    """Measure the panel, then erase what was measured.

    Measuring comes first and finishes first: a card is found by the two lines of
    text in it, so erasing a name before the last measurement would leave the
    tile it belongs to unfindable.

    Returns the labels, the item geometry and the slot geometry, with `im` edited
    in place.
    """
    aspect = im.height / im.width          # 1% of height is `aspect`% of width
    unify_back(im, panel)
    align_pairs(im, panel)

    # --- measure -----------------------------------------------------------
    fixed = []
    for entry in LAYERS.get(panel, []):
        x, y, w, h, text, align, run = entry[:7]
        box = fit(im, (x, y, w, h), run)
        if box is None:
            print("  ! nothing found for %r" % text)
            continue
        fixed.append((box, label(im, box, text, align, aspect,
                                 span=entry[8] if len(entry) > 8 else None,
                                 radius=entry[7] if len(entry) > 7 else None)))

    for group in LABEL_ROWS.get(panel, []):
        row = [g for _, g in fixed if "|".join(g["t"]) in group]
        if len(row) < 2:
            continue
        y = sorted(i["y"] for i in row)[len(row) // 2]
        h = sorted(i["h"] for i in row)[len(row) // 2]
        size = min(i["s"] for i in row)
        for i in row:
            i["y"], i["h"], i["s"] = y, h, size

    grid = []                              # one entry per row of tiles
    for ri, (row_y, row_h) in enumerate(NAME_ROWS.get(panel, [])):
        row = []
        for ci, (left, right) in enumerate(COLS):
            ko, en, price = ITEMS[panel][ri * 4 + ci]
            tile = card_of(im, (left - 1.1, TILE_ROWS[panel][ri][0] - 1.5,
                                right + 1.1, TILE_ROWS[panel][ri][1] + 0.8))
            name = fit(im, (left, row_y, right - left, row_h), None)
            if not tile or not name:
                print("  ! %s: tile=%s name=%s" % (ko, bool(tile), bool(name)))
                continue
            row.append({"ko": ko, "en": en, "price": price, "tile": tile,
                        "name": name, "col": ci,
                        "span": (left + 0.4, right - left - 0.8)})
        grid.append(row)

    slot_cards = []
    for key, window in SLOTS.get(panel, []):
        got = card_of(im, window)
        if not got:
            print("  ! no %s card found" % key)
            continue
        slot_cards.append((key, got))

    # --- item photos -------------------------------------------------------
    # The grid is uniform by design, so each photo box is taken from what the
    # tiles agree on rather than from its own tile alone. Tile by tile the
    # detection is not reliable enough for it: a photo whose own background is
    # white at the bottom (the fries, the milk) merges into the card's white
    # strip, and one that is white at the top (again the fries) leaves the card's
    # top edge invisible against the panel — which measured some photos short and
    # a few of them as nothing at all. Per row the true edges are the outermost
    # ones; per column, what the two rows agree on.
    items = {}
    if grid and any(grid):
        cols = {}
        for row in grid:
            for e in row:
                cols.setdefault(e["col"], []).append(e["tile"]["card"])
        span = {ci: (sorted(c[0] for c in boxes)[len(boxes) // 2],
                     sorted(c[2] for c in boxes)[len(boxes) // 2])
                for ci, boxes in cols.items()}
        for row in grid:
            if not row:
                continue
            top = min(e["tile"]["card"][1] for e in row)
            bottom = max(e["tile"]["strip"][1] for e in row)
            for e in row:
                x0, x1 = span[e["col"]]
                items[e["ko"]] = {"p": panel, "en": e["en"], "price": e["price"],
                                  "photo": list(as_pct(im, (x0, top, x1, bottom)))}

    # --- erase -------------------------------------------------------------
    draw = ImageDraw.Draw(im)
    labels, erased = [], []

    pix = im.load()

    def cover(box):
        """Erase a text box, one row at a time.

        Row by row rather than in one flat fill: the START button's face is a
        faint vertical gradient, and a single colour across it left a rectangle
        you could see. Each row takes the colour of the panel just outside the
        box at that same height, which is exact for a gradient and identical to a
        flat fill everywhere else.
        """
        bg = around_colour(im, box)
        x0, y0, x1, y1 = grow_flat(im, box, bg)
        # A grown box is a rectangle, and on a control the text nearly fills — the
        # delete key, the OK key — its corners end up outside the control's rounded
        # ones. Filling them then pushed square navy ears out past the key's curve.
        # So the box gives ground until all four of its corners are the colour it
        # is about to paint.
        off = lambda p: sum(abs(a - b) for a, b in zip(p, bg))
        for _ in range(14):
            corners = [pix[x, y] for x in (x0, x1 - 1) for y in (y0, y1 - 1)]
            if max(off(p) for p in corners) <= 30 or x1 - x0 < 8 or y1 - y0 < 8:
                break
            x0, y0, x1, y1 = x0 + 1, y0 + 1, x1 - 1, y1 - 1
        off = lambda p: sum(abs(a - b) for a, b in zip(p, bg))
        for y in range(y0, y1):
            # Only a sample that is plausibly the background may be used. On the
            # voucher card the box reaches down to where the card's own border
            # curves in, and both samples land on it: taking them anyway drew the
            # border's red straight across the card.
            sides = [p for p in (pix[max(0, x0 - 2), y], pix[min(im.width - 1, x1 + 1), y])
                     if off(p) <= 24]
            fill = (tuple(sum(c) // len(sides) for c in zip(*sides)) if sides
                    else tuple(bg[:3]))
            draw.line([(x0, y), (x1 - 1, y)], fill=fill)
        erased.append((x0, y0, x1, y1))

    for box, got in fixed:
        labels.append(got)
        cover(box)

    for row in grid:
        row_labels = []
        for e in row:
            row_labels.append(label(im, e["name"], e["en"], C, aspect, span=e["span"]))
            cover(e["name"])
        # one size per row: neighbouring names set in different sizes read as a
        # mistake, and the row is only as roomy as its longest name
        if row_labels:
            size = min(i["s"] for i in row_labels)
            for i in row_labels:
                i["s"] = size
            labels.extend(row_labels)
            # The card slots set their text from this, so it has to be kept: an
            # item's name on a card is the same design element as its name on the
            # tile, only in a card of a different width.
            tile_type.setdefault(panel, {"s": size,
                                         "w": as_pct(im, row[0]["tile"]["card"])[2]})

    # --- blank the cards that carry a fixed order --------------------------
    slots = []
    for key, got in slot_cards:
        card, strip = got["card"], got["strip"]
        radius = got["r"]
        # The card's own white, sampled from the clear band between the photo and
        # the name — the one part of the card with neither text nor photo in it.
        white = modal_colour(im, (strip[0] + radius, strip[1] + 2,
                                  strip[2] - radius, max(strip[1] + 4, got["name"][0] - 2)))
        ch = card[3] - card[1]
        frac = lambda v: round((v - card[1]) / ch * 100, 1)
        line = lambda run: (strip[0] + 4, run[0], strip[2] - 4, run[1])
        box = as_pct(im, card)
        # Type size comes from the menu tile, not from the height of the ink on
        # the card. Measured ink is the glyph body, and turning that back into a
        # font size needs a factor per typeface; the tiles already carry a size
        # that was fitted and checked, and a card is the same element in a
        # different width. The price keeps its own ratio to the name, which is a
        # property of the card as drawn.
        ref = tile_type.get(SLOT_SOURCE[key], {"s": 2.0, "w": box[2]})
        ns = ref["s"] * box[2] / ref["w"]
        name_h = got["name"][1] - got["name"][0]
        price_h = got["price"][1] - got["price"][0]
        slots.append({"k": key, "src": SLOT_SOURCE[key],
                      "x": box[0], "y": box[1], "w": box[2], "h": box[3],
                      "r": round(radius / im.width * 100, 2),
                      "photo": frac(strip[1]),
                      "name": [frac(got["name"][0]), frac(got["name"][1])],
                      "price": [frac(got["price"][0]), frac(got["price"][1])],
                      "ns": round(ns, 2),
                      "ps": round(ns * price_h / name_h, 2),
                      "nc": glyph_colour(im, line(got["name"]), white),
                      "pc": glyph_colour(im, line(got["price"]), white),
                      "cw": "#%02x%02x%02x" % white})
        print("     %-6s card=%s r=%d" % (key, box, radius))
        erase_card(im, card, around_colour(im, card, pad=6))
    return labels, items, slots, erased


def harmonise_slots(slots):
    """Give cards of the same shape the same insides.

    The three cards on the confirmation screen are one row of one component, and
    the collapsed headers are another, but each is measured on its own: a photo
    whose lower half is white (the hotcake, the milk) merges into the card's white
    strip and reads as a taller photo, which then pushed that card's name and
    price a percent below its neighbours'. Grouped by shape, the photo takes the
    deepest edge any of them showed and the text takes the middle one.
    """
    groups = {}
    for panel, row in slots.items():
        for s in row:
            groups.setdefault(round(s["w"]), []).append(s)
    for shape in groups.values():
        mid = lambda key, i: sorted(s[key][i] for s in shape)[len(shape) // 2]
        photo = max(s["photo"] for s in shape)
        name = [mid("name", 0), mid("name", 1)]
        price = [mid("price", 0), mid("price", 1)]
        # Radius and white are shared for the same reason: measured card by card
        # they come out a pixel or two apart, and the drink card's white picks up
        # a warm tint from the photograph that used to sit on it.
        radius = sorted(s["r"] for s in shape)[len(shape) // 2]
        white = max((s["cw"] for s in shape), key=lambda c: int(c[1:], 16))
        for s in shape:
            s["photo"], s["name"], s["price"] = photo, name, price
            s["r"], s["cw"] = radius, white
            s["ps"] = round(s["ns"] * (price[1] - price[0]) / (name[1] - name[0]), 2)
    return slots


def main():
    out_dir = PANELS
    out_js = OUT_JS
    if "--out" in sys.argv:
        out_dir = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(out_dir, exist_ok=True)
        out_js = os.path.join(out_dir, "kiosk-en.js")

    layers, items, slots, tile_type = {}, {}, {}, {}
    for n in range(1, 9):
        panel = "panel%02d" % n
        with Image.open(os.path.join(PANELS, panel + ".png")) as opened:
            im = trim_frame(opened.convert("RGB"))
        print("%s  %dx%d" % (panel, im.width, im.height))
        got_labels, got_items, got_slots, erased = build_panel(panel, im, tile_type)
        layers[panel] = got_labels
        items.update(got_items)
        if got_slots:
            slots[panel] = got_slots
        print("  %d labels, %d items, %d cards blanked, %d regions erased"
              % (len(got_labels), len(got_items), len(got_slots), len(erased)))
        if "--check" not in sys.argv:
            path = os.path.join(out_dir, panel + "-en.webp")
            # The site's usual quality. These panels carry less than the originals
            # did — no Korean, three fewer photographs — so they come out about a
            # third lighter even though nothing else changed.
            im.save(path, "WEBP", quality=86, method=6)
            print("  wrote %s  (%d KB)" % (os.path.basename(path),
                                           round(os.path.getsize(path) / 1024)))

    harmonise_slots(slots)

    nl = chr(10)
    header = ("/* Generated by scripts/build_kiosk_panels.py - do not edit by hand.",
              "   KIOSK_EN: English labels, positioned and sized from the Korean they",
              "   replace, which the panels no longer carry.",
              "   KIOSK_CARDS: the empty cards on those panels, and the menu photo to",
              "   draw into each one, so the screen shows what was actually chosen. */")
    body = (nl.join(header) + nl
            + "window.KIOSK_EN = " + json.dumps(layers, indent=0, ensure_ascii=False) + ";" + nl
            + "window.KIOSK_CARDS = "
            + json.dumps({"items": items, "slots": slots}, indent=0, ensure_ascii=False)
            + ";" + nl)
    if "--check" in sys.argv:
        current = open(out_js, encoding="utf-8").read() if os.path.exists(out_js) else ""
        if current != body:
            sys.exit("kiosk-en.js is out of date - run python scripts/build_kiosk_panels.py")
        print("kiosk-en.js up to date")
        return
    with open(out_js, "w", encoding="utf-8") as fh:
        fh.write(body)
    print("wrote %s  (%d panels, %d labels, %d items, %d card slots)"
          % (os.path.relpath(out_js, ROOT), len(layers),
             sum(len(v) for v in layers.values()), len(items),
             sum(len(v) for v in slots.values())))


if __name__ == "__main__":
    main()
