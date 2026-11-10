"""Builds the reverse-move command-bar button, SCReverseMove.tga.

A painted top-down view of a generic main battle tank (not one from the game) on desert
ground, gun pointing forward (up) while it backs away: its track marks and a cloud of sand
lie ahead of it, where it came from, and a red arrow behind it points the way it drives.
Every part is weathered with mud, dust and chipped paint by button_paint.material.

    python scripts/make-reverse-move-button.py

Writes resources/shared-control/Art/Textures/SCReverseMove.tga and a preview PNG beside it.
"""

import pathlib
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from button_paint import H, HS, S, W, WS, drop_shadow, lines, noise, p, paint, pts, save, vignette

rng = random.Random(7)      # fixed seed: the same picture every run

OLIVE = (104, 102, 70)
OLIVE_DARK = (80, 78, 54)
CAMO = (128, 112, 74)
STEEL = (62, 60, 54)
RUBBER = (40, 38, 34)
DARK = (22, 22, 16, 255)
CX = 30                     # tank centre line
TOP, BOTTOM = 7, 40         # hull front and rear


def terrain():
    base = Image.new("RGB", (WS, HS), (176, 146, 98))
    for scale, amount, seed in ((6 * S, 34, 1), (2 * S, 22, 2), (4, 14, 3)):
        base = ImageChops.add(base, noise(scale, amount, seed).convert("RGB"), offset=-128)
    d = ImageDraw.Draw(base)
    for _ in range(160):    # pebbles
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.2, 0.6)
        d.ellipse([p(x - r, y - r), p(x + r, y + r)], fill=rng.choice([(120, 98, 66), (206, 182, 140), (96, 80, 56)]))
    # track marks ahead of the tank: it came from there
    marks = Image.new("L", (WS, HS), 0)
    md = ImageDraw.Draw(marks)
    for x0 in (CX - 10.5, CX + 6.5):
        for y in range(-2, TOP + 2):
            md.rectangle([p(x0, y), p(x0 + 4, y + 0.5)], fill=110)
    marks = marks.filter(ImageFilter.GaussianBlur(S * 0.5))
    return Image.composite(Image.new("RGB", (WS, HS), (120, 96, 62)), base, marks).convert("RGBA")


def tank():
    v = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))

    # --- tracks: steel links with grousers ---
    for i, x0 in enumerate((CX - 11, CX + 6.6)):
        paint(v, lambda d, x0=x0: d.rectangle([p(x0, TOP + 0.5), p(x0 + 4.4, BOTTOM + 0.5)], fill=255), RUBBER, 10 + i, grime=1.0, chips=0)
        d = ImageDraw.Draw(v)
        y = TOP + 0.8
        while y < BOTTOM:
            d.rectangle([p(x0 + 0.4, y), p(x0 + 4.0, y + 0.35)], fill=(84, 80, 70, 255))
            d.rectangle([p(x0 + 1.8, y - 0.2), p(x0 + 2.6, y + 0.55)], fill=(28, 26, 22, 255))
            y += 1.1

    # --- hull with fenders ---
    hull = [(CX - 8.8, TOP + 2.2), (CX - 6.8, TOP), (CX + 6.8, TOP), (CX + 8.8, TOP + 2.2),
            (CX + 8.8, BOTTOM - 0.6), (CX + 7.6, BOTTOM), (CX - 7.6, BOTTOM), (CX - 8.8, BOTTOM - 0.6)]
    paint(v, lambda d: d.polygon(pts(hull), fill=255), OLIVE, 20, grime=0.6, camo=CAMO)
    for i, x0 in enumerate((CX - 11.6, CX + 8.6)):     # fenders over the tracks, with stowage bins
        paint(v, lambda d, x0=x0: d.rectangle([p(x0, TOP + 3), p(x0 + 3.0, BOTTOM - 1.5)], fill=255), OLIVE_DARK, 21 + i, grime=0.8, camo=CAMO)
        for j, y0 in enumerate((TOP + 5, TOP + 12, TOP + 22)):
            paint(v, lambda d, x0=x0, y0=y0: d.rectangle([p(x0 + 0.4, y0), p(x0 + 2.6, y0 + 5.5)], fill=255), OLIVE, 30 + i * 3 + j, grime=0.5)
    lines(v, [((CX - 8.4, TOP + 2.6), (CX + 8.4, TOP + 2.6))], (52, 50, 34, 255), 0.35)            # glacis edge
    for x in (CX - 5.5, CX + 5.5):                                                              # headlights
        paint(v, lambda d, x=x: d.rectangle([p(x - 0.7, TOP + 0.6), p(x + 0.7, TOP + 1.6)], fill=255), (190, 176, 120), int(40 + x), grime=0.2, edge=0.3)
    # engine deck with grilles, exhausts and a tow cable
    paint(v, lambda d: d.rectangle([p(CX - 7.2, 30), p(CX + 7.2, BOTTOM - 1)], fill=255), OLIVE_DARK, 45, grime=0.7)
    d = ImageDraw.Draw(v)
    for y in range(31, BOTTOM - 1):
        d.line([p(CX - 6.4, y + 0.2), p(CX - 0.6, y + 0.2)], fill=(36, 34, 24, 255), width=S // 3)
        d.line([p(CX + 0.6, y + 0.2), p(CX + 6.4, y + 0.2)], fill=(36, 34, 24, 255), width=S // 3)
    lines(v, [((CX - 7.4, 29.4), (CX + 7.4, 29.4))], (140, 132, 100, 255), 0.3)
    for x in (CX - 4.5, CX + 4.5):
        paint(v, lambda d, x=x: d.rectangle([p(x - 1.0, BOTTOM - 0.9), p(x + 1.0, BOTTOM + 0.3)], fill=255), (46, 42, 36), int(50 + x), grime=0.9, edge=0.4)
    cable = [(CX - 8.2, 12), (CX - 8.6, 18), (CX - 8.2, 26), (CX - 8.6, 32)]
    lines(v, list(zip(cable, cable[1:])), (60, 56, 44, 255), 0.4)

    # --- gun: long barrel with fume extractor and muzzle reference, drawn under the turret ---
    paint(v, lambda d: d.rectangle([p(CX - 0.75, -0.5), p(CX + 0.75, 18)], fill=255), OLIVE, 60, grime=0.15, chips=0.4)
    paint(v, lambda d: d.rectangle([p(CX - 1.15, 5.5), p(CX + 1.15, 8.5)], fill=255), OLIVE_DARK, 61, grime=0.1)
    paint(v, lambda d: d.rectangle([p(CX - 1.1, -0.5), p(CX + 1.1, 1.6)], fill=255), STEEL, 62, grime=0.1)

    # --- turret: angular, armour wedges at the front, bustle basket at the rear ---
    turret = [(CX - 3.2, 13.2), (CX + 3.2, 13.2), (CX + 6.6, 16.0), (CX + 7.0, 24.8), (CX + 5.6, 27.2),
              (CX - 5.6, 27.2), (CX - 7.0, 24.8), (CX - 6.6, 16.0)]
    paint(v, lambda d: d.polygon(pts(turret), fill=255), OLIVE, 70, grime=0.35, camo=CAMO)
    paint(v, lambda d: d.polygon(pts([(CX - 2.4, 13.4), (CX + 2.4, 13.4), (CX + 2.0, 16.6), (CX - 2.0, 16.6)]), fill=255), OLIVE_DARK, 71, grime=0.2)  # mantlet
    paint(v, lambda d: d.rectangle([p(CX - 5.0, 27.0), p(CX + 5.0, 29.6)], fill=255), OLIVE_DARK, 72, grime=0.6)  # bustle basket
    lines(v, [((CX - 4.6, 28.3), (CX + 4.6, 28.3))] + [((x, 27.2), (x, 29.4)) for x in (CX - 3, CX - 1, CX + 1, CX + 3)], (40, 38, 26, 255), 0.22)
    # roof kit kept off the centre line and to one side, so it never reads as a face
    paint(v, lambda d: d.ellipse([p(CX + 2.0, 21.6), p(CX + 5.4, 25.0)], fill=255), OLIVE_DARK, 73, grime=0.2)   # commander's cupola
    lines(v, [((CX + 3.7, 21.8), (CX + 3.7, 19.2))], DARK, 0.45)                                             # cupola MG
    paint(v, lambda d: d.rectangle([p(CX - 5.2, 23.0), p(CX - 2.2, 25.6)], fill=255), OLIVE_DARK, 74, grime=0.4)  # stowage box
    paint(v, lambda d: d.rectangle([p(CX + 2.6, 16.2), p(CX + 4.2, 17.6)], fill=255), STEEL, 75, grime=0.2)      # gunner's sight
    for i, (x, y) in enumerate(((CX - 6.4, 17.2), (CX - 6.6, 18.6), (CX + 6.4, 17.2), (CX + 6.6, 18.6))):     # smoke dischargers
        paint(v, lambda d, x=x, y=y: d.ellipse([p(x - 0.55, y - 0.55), p(x + 0.55, y + 0.55)], fill=255), STEEL, 80 + i, grime=0.2, edge=0.3)
    lines(v, [((CX + 5.2, 25.8), (CX + 5.6, 26.4)), ((CX - 5.2, 25.8), (CX - 5.6, 26.4))], DARK, 0.5)          # antenna bases
    return v


def front_dust(img):
    """Sand thrown up off the tracks, trailing ahead of the tank (up): it is backing away from there."""
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    front = TOP + 2
    for _ in range(170):
        y = rng.uniform(-1, front + 1)
        spread = (front + 2 - y) * 1.1
        x = rng.choice((CX - 9, CX + 9)) + rng.uniform(-spread, spread) * 0.6 + rng.uniform(-1.5, 1.5)
        r = rng.uniform(1.0, 2.4) + (front - y) * 0.16
        a = int(max(90, 225 - (front - y) * 11))
        d.ellipse([p(x - r, y - r), p(x + r, y + r)], fill=rng.choice([(222, 200, 156), (236, 218, 178), (204, 178, 130)]) + (a,))
    for _ in range(70):     # grains flung out
        y = rng.uniform(0, front)
        x = rng.choice((CX - 9, CX + 9)) + rng.uniform(-8, 8)
        d.ellipse([p(x - 0.25, y - 0.25), p(x + 0.25, y + 0.25)], fill=(240, 226, 190, 220))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(S * 0.5)))


def arrow(img):
    """Red arrow behind the tank, pointing back (down): the way it is driving."""
    d = ImageDraw.Draw(img)
    outline, amber = (30, 4, 4, 255), (226, 40, 36, 255)   # red, as the slayer reticle
    d.rectangle([p(CX - 2.6, 40.6), p(CX + 2.6, 43.4)], fill=outline)
    d.polygon(pts([(CX - 7.6, 42.4), (CX + 7.6, 42.4), (CX, 47.9)]), fill=outline)
    d.rectangle([p(CX - 1.8, 41.2), p(CX + 1.8, 43.2)], fill=amber)
    d.polygon(pts([(CX - 6.0, 43.0), (CX + 6.0, 43.0), (CX, 47.0)]), fill=amber)


def main():
    img = terrain()
    body = tank()
    drop_shadow(img, body, 1.4 * S, 1.4 * S, S * 0.8, alpha=130)
    img.alpha_composite(body)
    front_dust(img)
    img = vignette(img)
    arrow(img)
    save(img, pathlib.Path(__file__).resolve().parent.parent, "SCReverseMove")


if __name__ == "__main__":
    main()
