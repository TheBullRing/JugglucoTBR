"""Regenerates preview, icon and Play Store images (drawn mock-ups of the layout).

Run: python tools/generate_assets.py   (needs Pillow)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "app/src/main/res"
DRAW = RES / "drawable-nodpi"
STORE = ROOT / "docs/play-store"
PREV = ROOT / "docs/previews"
for p in (DRAW, STORE, PREV):
    p.mkdir(parents=True, exist_ok=True)
BOLD = str(RES / "font/inter_bold.ttf")
REG = str(RES / "font/inter_regular.ttf")
ACCENT = (0x62, 0xA8, 0xFF)
WHITE = (255, 255, 255)
GREY = (0xC0, 0xC0, 0xC0)
DATE_COL = (0xE0, 0xE0, 0xE0)
CELL_TEXT = (0xD8, 0xD8, 0xD8)
CELL_TITLE = (0x90, 0x90, 0x90)
CELL_ICON = (0xB8, 0xB8, 0xB8)
BAT_GREEN = (0x5F, 0xBF, 0x7A)
SS = 2  # supersample
N = 450


def font(path, size):
    return ImageFont.truetype(path, int(size * SS))


def text(d, x, y, s, f, fill, anchor="mm"):
    d.text((x * SS, y * SS), s, font=f, fill=fill, anchor=anchor)


def arrow(d, ax, ay, k=1.6):
    """Up-right trend arrow centred on (ax, ay); k scales the original 32 px design."""
    def p(dx, dy):
        return ((ax + dx * k) * SS, (ay + dy * k) * SS)
    d.line([p(-12, 12), p(8, -8)], fill=ACCENT, width=int(6 * k * SS))
    d.polygon([p(14, -14), p(14, 2), p(-2, -14)], fill=ACCENT)


def render(shape, ambient):
    """Mirrors the geometry in tools/generate_watchface.py (450x450 canvas)."""
    img = Image.new("RGB", (N * SS, N * SS), (0, 0, 0))
    d = ImageDraw.Draw(img)
    baseline = 60 + 116 / 2 + 0.364 * 96            # time baseline (152.9)
    if ambient:
        text(d, 225, baseline, "17:51", font(REG, 96), WHITE, anchor="ms")
    else:
        text(d, 338, baseline, "17:51", font(BOLD, 96), WHITE, anchor="rs")
        text(d, 342, baseline, ":32", font(BOLD, 36), GREY, anchor="ls")
    # glucose slot (kept in AOD): y=148, h=104; value right edge x=272, arrow box x=280..340 (60 px)
    gy, gh = 148, 104
    text(d, 272, gy + gh / 2 + 0.364 * 84, "128", font(BOLD, 84), ACCENT, anchor="rs")
    arrow(d, 310, gy + gh / 2, k=1.9)
    if not ambient:
        text(d, 225, 42 + 17, "SAT 15 NOV", font(BOLD, 26), DATE_COL)
        text(d, 348, gy + gh / 2 + 0.364 * 28, "+8", font(REG, 28), GREY, anchor="ls")
        text(d, 225, 240 + 20, "0 min ago", font(REG, 32), GREY)
        left, right, r1, r2, ch = 85, 235, 284, 338, 46
        f, ft = font(REG, 22), font(REG, 13)
        # row 1: weather | next event (icon + value + caption)
        sun = Image.open(RES / "drawable-nodpi/ic_sunny.png").convert("RGBA").resize((30 * SS, 30 * SS), Image.LANCZOS)
        img.paste(sun, ((left + 8) * SS, (r1 + 8) * SS), sun)
        text(d, left + 44, r1 + ch / 2, "19\u00b0", f, CELL_TEXT, anchor="lm")
        d.rounded_rectangle([(right + 10) * SS, (r1 + 10) * SS, (right + 36) * SS, (r1 + 36) * SS], radius=4 * SS,
                            outline=CELL_ICON, width=2 * SS)
        text(d, right + 44, r1 + 15, "18:12", f, CELL_TEXT, anchor="lm")
        text(d, right + 44, r1 + 36, "Next event", ft, CELL_TITLE, anchor="lm")
        # row 2: steps | battery (green >= 50, yellow >= 20, red below)
        d.ellipse([(left + 14) * SS, (r2 + 11) * SS, (left + 34) * SS, (r2 + 35) * SS], outline=CELL_ICON, width=2 * SS)
        text(d, left + 44, r2 + 15, "3168", f, CELL_TEXT, anchor="lm")
        text(d, left + 44, r2 + 36, "Steps", ft, CELL_TITLE, anchor="lm")
        bx, by = right + 10, r2 + (ch - 13) / 2
        d.rectangle([bx * SS, by * SS, (bx + 24) * SS, (by + 13) * SS], outline=BAT_GREEN, width=int(1.5 * SS))
        d.rectangle([(bx + 24) * SS, (by + 3.5) * SS, (bx + 26.5) * SS, (by + 9.5) * SS], fill=BAT_GREEN)
        d.rectangle([(bx + 2.5) * SS, (by + 2.5) * SS, (bx + 2.5 + 19 * .97) * SS, (by + 10.5) * SS], fill=BAT_GREEN)
        text(d, right + 44, r2 + ch / 2, "97%", f, BAT_GREEN, anchor="lm")
    img = img.resize((N, N), Image.LANCZOS)
    mask = Image.new("L", (N * 4, N * 4), 0)
    md = ImageDraw.Draw(mask)
    if shape == "round":
        md.ellipse([0, 0, N * 4 - 1, N * 4 - 1], fill=255)
    elif shape == "square":
        md.rounded_rectangle([0, 0, N * 4 - 1, N * 4 - 1], radius=60 * 4, fill=255)
    else:
        return img
    mask = mask.resize((N, N), Image.LANCZOS)
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


render("round", False).save(DRAW / "preview.png")
render("round", False).save(PREV / "preview_round.png")
render("square", False).save(PREV / "preview_square.png")
render("round", True).save(PREV / "preview_ambient.png")


def icon(size):
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    d.ellipse([s * .06, s * .06, s * .94, s * .94], outline=ACCENT, width=int(s * .035))
    d.text((s / 2, s * .5), "126", font=ImageFont.truetype(BOLD, int(s * .34)), fill=ACCENT, anchor="mm")
    return im.resize((size, size), Image.LANCZOS)


icon(192).save(DRAW / "icon.png")
icon(512).save(STORE / "icon_512.png")

fg = Image.new("RGB", (1024, 500), (0, 0, 0))
fd = ImageDraw.Draw(fg)
face = render("round", False).resize((420, 420), Image.LANCZOS)
fg.paste(face, (70, 40), face)
fd.text((540, 190), "JugglucoTBR", font=ImageFont.truetype(BOLD, 72), fill=WHITE, anchor="lm")
fd.text((540, 270), "Glucose at a glance on Wear OS", font=ImageFont.truetype(REG, 30), fill=ACCENT, anchor="lm")
fg.save(STORE / "feature_graphic_1024x500.png")
render("round", False).resize((384, 384), Image.LANCZOS).save(STORE / "screenshot_1_interactive.png")
render("round", True).resize((384, 384), Image.LANCZOS).save(STORE / "screenshot_2_ambient.png")
print("ok")
