"""Builds the artillery-slayer command-bar button, SCArtillerySlayer.tga.

A painted side view of a generic self-propelled howitzer (not one from the game) on desert
ground, barrel raised high, under a red scope reticle with a black outline. Every part is
weathered with mud, dust and chipped paint by button_paint.material.

    python scripts/make-artillery-slayer-button.py

Writes resources/shared-control/Art/Textures/SCArtillerySlayer.tga and a preview PNG beside it.
"""

import math
import pathlib
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from button_paint import H, HS, S, W, WS, drop_shadow, lines, noise, p, paint, pts, save, vignette

GROUND = 34                 # horizon line
rng = random.Random(11)     # fixed seed: the same picture every run

OLIVE = (104, 102, 70)
OLIVE_DARK = (80, 78, 54)
CAMO = (128, 112, 74)
STEEL = (62, 60, 54)
RUBBER = (40, 38, 34)
DARK = (22, 22, 16, 255)


def scene():
    img = Image.new("RGB", (WS, HS))
    d = ImageDraw.Draw(img)
    for y in range(HS):
        if y < GROUND * S:
            t = y / (GROUND * S)
            c = (int(146 + 70 * t), int(154 + 44 * t), int(160 + 2 * t))       # hazy sky
        else:
            t = (y - GROUND * S) / (HS - GROUND * S)
            c = (int(192 - 52 * t), int(162 - 50 * t), int(112 - 38 * t))     # sand
        d.line([(0, y), (WS, y)], fill=c)
    dunes = [(0, GROUND)] + [(x, GROUND - 2.5 - 1.8 * math.sin(x / 6.5 + 1)) for x in range(0, W + 1)] + [(W, GROUND)]
    d.polygon(pts(dunes), fill=(184, 156, 114))
    sand = Image.new("L", (WS, HS), 0)
    ImageDraw.Draw(sand).rectangle([p(0, GROUND - 5), p(W, H)], fill=255)
    for scale, amount, seed in ((4 * S, 26, 1), (S, 18, 2), (3, 12, 3)):
        img = Image.composite(ImageChops.add(img, noise(scale, amount, seed).convert("RGB"), offset=-128), img, sand)
    d = ImageDraw.Draw(img)
    for _ in range(90):     # pebbles, smaller toward the horizon
        y = rng.uniform(GROUND + 0.5, H)
        r = 0.15 + (y - GROUND) * 0.045
        x = rng.uniform(0, W)
        d.ellipse([p(x - r, y - r * 0.6), p(x + r, y + r * 0.6)], fill=rng.choice([(104, 84, 56), (214, 190, 146), (120, 104, 70)]))
    return img.convert("RGBA")


def howitzer():
    v = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))

    # --- gun, drawn first so the mantlet and turret cover its root ---
    pivot, ang, length = (21.5, 20.2), math.radians(-142), 27.0

    def at(t, off):
        return (pivot[0] + math.cos(ang) * t - math.sin(ang) * off, pivot[1] + math.sin(ang) * t + math.cos(ang) * off)

    def quad(t0, t1, w0, w1):
        return [at(t0, -w0), at(t1, -w1), at(t1, w1), at(t0, w0)]

    paint(v, lambda d: d.polygon(pts(quad(0, length - 2.6, 1.05, 0.72)), fill=255), OLIVE, 21, grime=0.15, chips=0.4)
    paint(v, lambda d: d.polygon(pts(quad(9.5, 13.0, 1.35, 1.35)), fill=255), OLIVE_DARK, 22, grime=0.1)      # fume extractor
    paint(v, lambda d: d.polygon(pts(quad(length - 3.0, length, 1.35, 1.35)), fill=255), STEEL, 23, grime=0.1)  # muzzle brake
    for t in (length - 2.3, length - 1.1):      # brake ports
        lines(v, [(at(t, -1.3), at(t, 1.3))], DARK, 0.35)
    paint(v, lambda d: d.polygon(pts(quad(-1.0, 3.2, 2.2, 1.7)), fill=255), OLIVE_DARK, 24, grime=0.2)        # mantlet

    # --- running gear ---
    paint(v, lambda d: d.rounded_rectangle([p(6.5, 28.6), p(48.5, 36.2)], radius=int(3.6 * S), fill=255), RUBBER, 30, grime=0.9, chips=0)
    tread = ImageDraw.Draw(v)
    for x in range(8, 48):                      # track links along the bottom and top run
        tread.rectangle([p(x, 35.6), p(x + 0.5, 36.4)], fill=(30, 28, 24, 255))
        tread.rectangle([p(x + 0.2, 28.3), p(x + 0.6, 28.9)], fill=(30, 28, 24, 255))
    for i, x in enumerate((12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5)):
        paint(v, lambda d, x=x: d.ellipse([p(x - 2.3, 30.0), p(x + 2.3, 34.6)], fill=255), (72, 70, 60), 40 + i, grime=0.8, chips=0.2)
        paint(v, lambda d, x=x: d.ellipse([p(x - 1.0, 31.3), p(x + 1.0, 33.3)], fill=255), (54, 52, 44), 50 + i, grime=0.5, edge=0.5)
    sprocket = [(8.6 + 2.3 * math.cos(a * math.pi / 6) * (1.0 if a % 2 else 0.78),
                 31.9 + 2.3 * math.sin(a * math.pi / 6) * (1.0 if a % 2 else 0.78)) for a in range(12)]
    paint(v, lambda d: d.polygon(pts(sprocket), fill=255), STEEL, 60, grime=0.7)
    paint(v, lambda d: d.ellipse([p(45.0, 30.4), p(48.0, 33.4)], fill=255), STEEL, 61, grime=0.7)        # idler
    for x in (17, 27, 37):                      # return rollers
        paint(v, lambda d, x=x: d.ellipse([p(x - 0.8, 28.5), p(x + 0.8, 30.1)], fill=255), STEEL, 62 + x, grime=0.4, edge=0.4)

    # --- hull ---
    hull = [(5.8, 25.6), (10.5, 22.2), (47.2, 22.2), (49.0, 24.0), (49.0, 29.4), (8.0, 29.4), (5.8, 27.4)]
    paint(v, lambda d: d.polygon(pts(hull), fill=255), OLIVE, 70, grime=0.75, camo=CAMO)
    skirt = [(9.0, 26.0), (48.2, 26.0), (48.2, 30.4), (40.0, 30.6), (39.4, 30.2), (24.0, 30.3), (23.2, 30.7), (9.6, 30.4)]
    paint(v, lambda d: d.polygon(pts(skirt), fill=255), OLIVE_DARK, 71, grime=1.0, camo=CAMO)
    lines(v, [((x, 26.3), (x, 30.2)) for x in (15.5, 22, 29, 35.5, 42)], (40, 38, 26, 255), 0.25)      # skirt seams
    for x in range(11, 48, 3):                  # bolts
        ImageDraw.Draw(v).ellipse([p(x - 0.2, 26.6), p(x + 0.2, 27.0)], fill=(150, 146, 108, 255))
    paint(v, lambda d: d.rectangle([p(6.8, 24.6), p(8.2, 25.6)], fill=255), (190, 176, 120), 72, grime=0.2, edge=0.3)  # headlight
    paint(v, lambda d: d.rectangle([p(13, 20.8), p(19, 22.3)], fill=255), OLIVE_DARK, 73, grime=0.4)     # front stowage
    lines(v, [((5.2, 27.6), (7.0, 27.6))], DARK, 0.6)                                                   # tow hook

    # --- turret: big box with a rear bustle, stowage and fittings ---
    turret = [(20.5, 22.4), (22.0, 15.6), (24.5, 14.2), (43.5, 14.2), (46.2, 15.2), (47.0, 20.5), (45.0, 22.4)]
    paint(v, lambda d: d.polygon(pts(turret), fill=255), OLIVE, 80, grime=0.45, camo=CAMO)
    paint(v, lambda d: d.rectangle([p(30, 17.4), p(38.5, 21.0)], fill=255), OLIVE_DARK, 81, grime=0.5)   # side stowage box
    lines(v, [((30.2, 19.2), (38.3, 19.2))], (44, 42, 30, 255), 0.25)
    lines(v, [((24.5, 16.8), (44.5, 16.8))], (150, 146, 106, 255), 0.3)                                 # handrail
    for x in (25.5, 31, 37, 43):
        lines(v, [((x, 16.8), (x, 17.5))], (150, 146, 106, 255), 0.25)
    paint(v, lambda d: d.rectangle([p(39.5, 12.2), p(43.5, 14.4)], fill=255), OLIVE_DARK, 82, grime=0.3)  # cupola
    lines(v, [((40.0, 12.7), (36.5, 12.4))], DARK, 0.45)                                                # roof MG
    paint(v, lambda d: d.rectangle([p(27, 13.0), p(30.5, 14.4)], fill=255), OLIVE_DARK, 83, grime=0.3)    # sight box
    for i, x in enumerate((22.6, 23.6)):        # smoke dischargers
        paint(v, lambda d, x=x: d.ellipse([p(x - 0.5, 16.2), p(x + 0.5, 17.4)], fill=255), STEEL, 84 + i, grime=0.2, edge=0.3)
    lines(v, [((44.5, 14.2), (45.6, 6.8)), ((42.2, 14.2), (42.8, 9.6))], (30, 30, 24, 255), 0.22)       # antennas
    paint(v, lambda d: d.rectangle([p(46.6, 15.6), p(48.8, 20.0)], fill=255), OLIVE_DARK, 86, grime=0.6)  # bustle rack
    lines(v, [((46.8, 17.6), (48.6, 17.6))], (44, 42, 30, 255), 0.25)
    return v


def dust_cloud(img):
    """Light dust hanging around the tracks."""
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(40):
        x = rng.uniform(4, 52)
        y = rng.uniform(33.5, 37.5)
        r = rng.uniform(0.8, 2.0)
        d.ellipse([p(x - r, y - r * 0.6), p(x + r, y + r * 0.6)], fill=(214, 192, 148, rng.randint(40, 90)))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(S * 0.6)))


def reticle():
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = 28.5, 24, 16
    red, black = (226, 40, 36, 255), (0, 0, 0, 255)
    for color, w in ((black, 1.6), (red, 0.8)):
        d.ellipse([p(cx - r, cy - r), p(cx + r, cy + r)], outline=color, width=int(w * S))
        for x0, y0, x1, y1 in ((cx, cy - r - 3, cx, cy - 5), (cx, cy + 5, cx, cy + r + 3),
                               (cx - r - 3, cy, cx - 5, cy), (cx + 5, cy, cx + r + 3, cy)):
            d.line([p(x0, y0), p(x1, y1)], fill=color, width=int(w * S))
    d.ellipse([p(cx - 1.1, cy - 1.1), p(cx + 1.1, cy + 1.1)], fill=black)
    d.ellipse([p(cx - 0.6, cy - 0.6), p(cx + 0.6, cy + 0.6)], fill=red)
    return layer


def main():
    img = scene()
    gun = howitzer()
    ground_shadow = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    ImageDraw.Draw(ground_shadow).ellipse([p(4, 34.5), p(53, 38.5)], fill=(40, 28, 12, 160))
    img.alpha_composite(ground_shadow.filter(ImageFilter.GaussianBlur(S)))
    drop_shadow(img, gun, 0.6 * S, 0.6 * S, S * 0.6, alpha=90)
    img.alpha_composite(gun)
    dust_cloud(img)
    img.alpha_composite(reticle())
    img = vignette(img)
    save(img, pathlib.Path(__file__).resolve().parent.parent, "SCArtillerySlayer")


if __name__ == "__main__":
    main()
