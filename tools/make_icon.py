#!/usr/bin/env python3
"""Draw the plugin's store icon.

The icon is generated rather than hand-drawn so it can be tweaked and rebuilt
instead of being an unexplained binary in the repo:

    python3 tools/make_icon.py

Outputs icon.png (512), icon-256.png and icon-128.png beside the script's parent
directory. Everything is drawn at 4x and downsampled with Lanczos, which is where
the smooth edges come from — there is no SVG rasteriser in the build image, and a
second hand-maintained SVG would drift from this.

Design: the designer's cube on the left, yours on the right, with a convert arrow
between — the plugin's whole job in one mark, readable without a caption.
Deliberately warmer and bolder than the FlashForge device plugin's icon (a cooler
blue cube with a LAN signal mark), because the two plugins are otherwise unrelated
and at hub-tile size they have to be told apart at a glance rather than read.

A circular-arrow-around-a-cube was tried first and abandoned: rendered as ASCII it
had its two arc gaps at the sides, which at 128 px reads as broken strokes rather
than a ring. Two simple shapes beat three fussy ones.
"""

import math
import os

from PIL import Image, ImageDraw

SS = 4                     # supersample factor
OUT = 512                  # final edge length
S = OUT * SS

BG_TOP = (74, 38, 20)
BG_BOTTOM = (17, 12, 10)
AMBER = (255, 172, 66)
AMBER_DIM = (198, 112, 34)
GHOST = (214, 168, 122)
WHITE = (255, 250, 242)

# Pillow renamed the resampling constants; keep working on both sides of 9.1.
try:
    RESAMPLE = Image.Resampling.LANCZOS
    BICUBIC = Image.Resampling.BICUBIC
except AttributeError:                                   # Pillow < 9.1
    RESAMPLE = Image.LANCZOS
    BICUBIC = Image.BICUBIC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1],
                                        radius=radius, fill=255)
    return m


def background():
    """A vertical gradient, clipped to a rounded square."""
    strip = Image.new("RGB", (1, S))
    px = strip.load()
    for y in range(S):
        t = (y / (S - 1)) ** 0.85
        px[0, y] = tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM))
    grad = strip.resize((S, S), BICUBIC)

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.paste(grad, (0, 0), rounded_mask(S, int(S * 0.225)))
    return img


def draw_cube(d, cx, cy, w, h, dep, filled=True, lines=False):
    """An isometric cube, drawn solid or as an outline.

    The layer gaps are optional: they read as printing at 512 and turn to mud below
    about 192, so the small sizes get a clean silhouette instead.
    """
    top = (cx, cy)
    right = (cx + w, cy + h / 2)
    bottom = (cx, cy + h)
    left = (cx - w, cy + h / 2)
    deep_l = (cx - w, cy + h / 2 + dep)
    deep_r = (cx + w, cy + h / 2 + dep)
    deep_b = (cx, cy + h + dep)

    if filled:
        d.polygon([right, bottom, deep_b, deep_r], fill=AMBER_DIM)
        d.polygon([left, bottom, deep_b, deep_l], fill=AMBER)
        d.polygon([top, right, bottom, left], fill=WHITE)
    else:
        edge = GHOST
        for face in ([top, right, bottom, left],
                     [left, bottom, deep_b, deep_l],
                     [right, bottom, deep_b, deep_r]):
            d.polygon(face, outline=edge, width=max(2, int(S * 0.019)))

    if not lines:
        return
    line_w = max(1, int(S * 0.011))
    for frac in (1 / 3, 2 / 3):
        yl = frac * dep
        d.line([(cx - w, cy + h / 2 + yl), (cx, cy + h + yl)],
               fill=(40, 22, 12, 255), width=line_w)
        d.line([(cx + w, cy + h / 2 + yl), (cx, cy + h + yl)],
               fill=(40, 22, 12, 255), width=line_w)


def draw_arrow(d, x, y, size):
    """A solid arrow pointing right: the conversion itself.

    The tail stops well short of the cube beside it — a longer one read as part of
    the cube rather than as an arrow, which is exactly what the first render did.
    """
    d.rectangle([x - size * 0.72, y - size * 0.19,
                 x + size * 0.10, y + size * 0.19], fill=WHITE)
    d.polygon([(x - size * 0.05, y - size * 0.60),
               (x - size * 0.05, y + size * 0.60),
               (x + size * 0.60, y)], fill=WHITE)


def main():
    img = background()
    d = ImageDraw.Draw(img)

    # Three marks across one row, sized to leave a margin on every side. The left
    # cube is the outline of the project you were given; the right is yours.
    w, h, dep = S * 0.176, S * 0.262, S * 0.153
    cy = S * 0.5 - (h + dep) / 2
    draw_cube(d, S * 0.238, cy, w, h, dep, filled=False)
    draw_arrow(d, S * 0.5, cy + (h + dep) / 2, S * 0.100)
    draw_cube(d, S * 0.762, cy, w, h, dep, filled=True)

    final = img.resize((OUT, OUT), RESAMPLE)

    main_path = os.path.join(ROOT, "icon.png")
    final.save(main_path)
    print("wrote", main_path, final.size)

    for size in (256, 128):
        p = os.path.join(ROOT, f"icon-{size}.png")
        final.resize((size, size), RESAMPLE).save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
