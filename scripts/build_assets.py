"""Generate derived image assets for the site.

Outputs (all regenerated from committed source images, safe to re-run):
  assets/news/thumbs/<name>.webp     720px-wide thumbnails for the news list
  assets/bogyeom-park-224.webp       sidebar portrait (displayed at 72-112px)
  assets/favicon.ico                 16/32/48/64 monogram icon
  assets/apple-touch-icon.png        180px flat monogram icon
  assets/og-card.jpg                 1200x630 link-preview card

Source images are never modified; the full-size originals stay in place because
the news list links to them.

Usage:  python scripts/build_assets.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# Palette lifted from assets/site.css so generated art matches the site.
INK = "#17252a"
FEATURE_BG = "#12343c"
ACCENT = "#0f6b78"
ACCENT_PALE = "#9bd1d5"
PAPER_TINT = "#d9e8ea"
MUTED_TINT = "#7fb3ba"

FONTS = {
    "georgia": r"C:\Windows\Fonts\georgia.ttf",
    "georgia_bold": r"C:\Windows\Fonts\georgiab.ttf",
    "malgun": r"C:\Windows\Fonts\malgun.ttf",
    "ui": r"C:\Windows\Fonts\segoeui.ttf",
    "ui_semibold": r"C:\Windows\Fonts\seguisb.ttf",
}

# Text-heavy scans (award certificates) keep a higher quality floor.
HIGH_QUALITY_STEMS = {"hci-korea-best-paper-2025"}

THUMB_WIDTH = 720
# Paper figures carry text, so they keep more width than a photo thumbnail.
FIGURE_WIDTH = 1400


def font(name, size):
    return ImageFont.truetype(FONTS[name], size)


def load_upright(path):
    """Open an image with its EXIF rotation baked into the pixels.

    Phone photos store rotation as an EXIF tag rather than rotating the pixels.
    Browsers honour that tag on the original JPEG, but re-encoding drops it — so
    without this the derived thumbnail comes out sideways (chi-2025.jpg is
    orientation 6).
    """
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


def kb(path):
    return int(round(os.path.getsize(path) / 1024))


def build_news_thumbs():
    src_dir = os.path.join(ASSETS, "news")
    out_dir = os.path.join(src_dir, "thumbs")
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    for name in sorted(os.listdir(src_dir)):
        src = os.path.join(src_dir, name)
        stem, ext = os.path.splitext(name)
        if not os.path.isfile(src) or ext.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        im = load_upright(src)
        if im.width > THUMB_WIDTH:
            height = round(im.height * THUMB_WIDTH / im.width)
            im = im.resize((THUMB_WIDTH, height), Image.LANCZOS)
        quality = 90 if stem in HIGH_QUALITY_STEMS else 80
        out = os.path.join(out_dir, stem + ".webp")
        im.save(out, "WEBP", quality=quality, method=6)
        rows.append((name, kb(src), stem + ".webp", kb(out), im.size))

    return rows


def build_portrait():
    src = os.path.join(ASSETS, "bogyeom-park.jpg")
    out = os.path.join(ASSETS, "bogyeom-park-224.webp")
    im = load_upright(src)
    height = round(im.height * 224 / im.width)
    im = im.resize((224, height), Image.LANCZOS)
    im.save(out, "WEBP", quality=88, method=6)
    return kb(src), kb(out)


def monogram(size, radius_ratio=0.19, letter="B"):
    """Render the monogram at `size` px on a rounded teal tile."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = round(size * radius_ratio)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=ACCENT)

    # Fit the letter to ~62% of the tile, then centre it on its ink extents
    # rather than its font metrics, so it sits optically centred.
    f = font("georgia_bold", round(size * 0.72))
    left, top, right, bottom = draw.textbbox((0, 0), letter, font=f)
    x = (size - (right - left)) / 2 - left
    y = (size - (bottom - top)) / 2 - top
    draw.text((x, y), letter, font=f, fill="white")
    return img


def build_icons():
    master = monogram(256)
    ico = os.path.join(ASSETS, "favicon.ico")
    master.save(ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    # Apple crops its own corners, so ship a full-bleed tile.
    flat = monogram(360, radius_ratio=0.0)
    apple = os.path.join(ASSETS, "apple-touch-icon.png")
    flat.resize((180, 180), Image.LANCZOS).convert("RGB").save(apple, "PNG")
    return kb(ico), kb(apple)


def draw_tracked_text(draw, xy, text, f, fill, tracking):
    """Draw text with extra letter spacing (Pillow has no tracking support)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def build_og_card():
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), FEATURE_BG)
    draw = ImageDraw.Draw(card)

    # Circular portrait on the right, with a hairline ring.
    diameter = 300
    cx, cy = 950, 315
    box = (cx - diameter // 2, cy - diameter // 2)
    photo = load_upright(os.path.join(ASSETS, "bogyeom-park.jpg"))
    side = min(photo.size)
    photo = photo.crop((
        (photo.width - side) // 2,
        (photo.height - side) // 2,
        (photo.width + side) // 2,
        (photo.height + side) // 2,
    )).resize((diameter, diameter), Image.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, diameter - 1, diameter - 1], fill=255)
    card.paste(photo, box, mask)
    draw.ellipse(
        [box[0] - 3, box[1] - 3, box[0] + diameter + 2, box[1] + diameter + 2],
        outline=(155, 209, 213), width=3,
    )

    x = 80
    draw_tracked_text(
        draw, (x, 168), "AGENTIC AI  ·  HUMAN–AI INTERACTION",
        font("ui_semibold", 22), ACCENT_PALE, 2.4,
    )
    draw.text((x, 222), "Bogyeom Park", font=font("georgia_bold", 84), fill="white")
    draw.text((x, 336), "박보겸", font=font("malgun", 34), fill=ACCENT_PALE)
    draw.text((x, 400), "Integrated Ph.D. Student", font=font("ui", 30), fill=PAPER_TINT)
    draw.text((x, 440), "SeoulTech HAI Lab", font=font("ui", 30), fill=PAPER_TINT)
    draw.line([x, 520, x + 54, 520], fill=ACCENT_PALE, width=4)
    draw.text((x, 546), "bogyeompark.github.io", font=font("ui", 24), fill=MUTED_TINT)

    out = os.path.join(ASSETS, "og-card.jpg")
    card.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return kb(out)


def build_publication_figures():
    """Re-encode paper figures for the web, keeping the originals as the source.

    They arrive at print resolution — two were over 2.5 MB — and the publications
    list loads all twelve at once. Figures are diagrams with text in them, so the
    width stays generous and the quality high; the saving comes from webp.
    """
    src_root = os.path.join(ASSETS, "publications")
    rows = []
    for slug in sorted(os.listdir(src_root)):
        folder = os.path.join(src_root, slug)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            stem, ext = os.path.splitext(name)
            if ext.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            src = os.path.join(folder, name)
            im = load_upright(src)
            if im.width > FIGURE_WIDTH:
                height = round(im.height * FIGURE_WIDTH / im.width)
                im = im.resize((FIGURE_WIDTH, height), Image.LANCZOS)
            out = os.path.join(folder, stem + ".webp")
            im.save(out, "WEBP", quality=86, method=6)
            rows.append((slug, name, kb(src), kb(out)))
    return rows


def build_cv_pages():
    """Rasterise the CV so the page can show it without a PDF viewer.

    A PDF in an <iframe> is blank on much of mobile Safari, and that is exactly
    where a CV gets opened. Rendering each page to an image shows the real
    document everywhere; the PDF itself stays one button away.
    """
    import fitz  # PyMuPDF

    src = os.path.join(ASSETS, "cv", "Bogyeom_Park_CV.pdf")
    out_dir = os.path.join(ASSETS, "cv", "pages")
    os.makedirs(out_dir, exist_ok=True)
    for stale in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, stale))

    rows = []
    with fitz.open(src) as doc:
        for index, page in enumerate(doc, 1):
            # 2x of the ~800px display width, so it stays sharp on retina
            zoom = 1600 / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            out = os.path.join(out_dir, "page-%d.webp" % index)
            image.save(out, "WEBP", quality=82, method=6)
            rows.append((index, image.size, kb(out)))
    return rows


def main():
    if not os.path.isdir(ASSETS):
        sys.exit("assets/ not found next to scripts/ — run from the repo")

    rows = build_news_thumbs()
    before = sum(r[1] for r in rows)
    after = sum(r[3] for r in rows)
    print("news thumbnails")
    for name, src_kb, out_name, out_kb, size in rows:
        print(f"  {name:<38} {src_kb:>6} KB -> thumbs/{out_name:<40} {out_kb:>4} KB  {size[0]}x{size[1]}")
    print(f"  {'total':<38} {before:>6} KB -> {'':<48} {after:>4} KB")

    src_kb, out_kb = build_portrait()
    print(f"portrait   bogyeom-park.jpg {src_kb} KB -> bogyeom-park-224.webp {out_kb} KB")

    ico_kb, apple_kb = build_icons()
    print(f"icons      favicon.ico {ico_kb} KB, apple-touch-icon.png {apple_kb} KB")

    print(f"og card    og-card.jpg {build_og_card()} KB")

    print("publication figures")
    before = after = 0
    for slug, name, src_kb, out_kb in build_publication_figures():
        before += src_kb
        after += out_kb
        print(f"  {slug}/{name:<34} {src_kb:>5} KB -> {out_kb:>4} KB")
    print(f"  {'total':<44} {before:>5} KB -> {after:>4} KB")

    print("cv pages")
    for index, size, size_kb in build_cv_pages():
        print(f"  page-{index}.webp  {size[0]}x{size[1]}  {size_kb} KB")


if __name__ == "__main__":
    main()
