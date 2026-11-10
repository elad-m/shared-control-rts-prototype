"""Builds the More and Back command-bar buttons, SCPageMore.tga and SCPageBack.tga.

A weathered steel plate with corner bolts and red double chevrons: pointing right for More
(go to the page with the extra buttons), left for Back. Plain Zero Hour and Escalated use
these; under ShockWave the game uses ShockWave's own One Down / One Up buttons instead.

    python scripts/make-page-buttons.py

Writes resources/shared-control/Art/Textures/SCPageMore.tga and SCPageBack.tga (plus previews).
"""

import pathlib

from PIL import Image, ImageDraw, ImageFilter

from button_paint import H, HS, S, W, WS, drop_shadow, mask_of, material, p, pts, save, vignette

STEEL = (88, 90, 82)


def chevrons(pointing_right):
    def shape(x):
        tip = 10.5
        if pointing_right:
            return [(x, 11), (x + 5, 11), (x + 5 + tip, 24), (x + 5, 37), (x, 37), (x + tip, 24)]
        return [(x + tip + 5, 11), (x + tip, 11), (x, 24), (x + tip, 37), (x + tip + 5, 37), (x + 5, 24)]
    return [shape(14), shape(28)]


def draw(pointing_right):
    img = Image.new("RGBA", (WS, HS), (0, 0, 0, 255))
    plate = mask_of(lambda d: d.rectangle([p(0, 0), p(W, H)], fill=255))
    img.alpha_composite(material(plate, STEEL, 5, grime=0.55, chips=0.6, edge=0.0, outline=0.0))
    # raised inner panel
    panel = mask_of(lambda d: d.rounded_rectangle([p(4.5, 4.5), p(W - 4.5, H - 4.5)], radius=2 * S, fill=255))
    img.alpha_composite(material(panel, (78, 80, 72), 6, grime=0.45, chips=0.5, edge=1.0, outline=0.6))
    # corner bolts
    for i, (x, y) in enumerate(((2.3, 2.3), (W - 2.3, 2.3), (2.3, H - 2.3), (W - 2.3, H - 2.3))):
        bolt = mask_of(lambda d, x=x, y=y: d.ellipse([p(x - 1.2, y - 1.2), p(x + 1.2, y + 1.2)], fill=255))
        img.alpha_composite(material(bolt, (120, 120, 110), 10 + i, grime=0.3, chips=0, edge=1.0, outline=0.8))
    # red chevrons with a dark outline and a little shadow, worn like stencilled paint
    arrows = mask_of(lambda d: [d.polygon(pts(c), fill=255) for c in chevrons(pointing_right)])
    outline = arrows.filter(ImageFilter.MaxFilter(13))
    dark = Image.new("RGBA", (WS, HS), (20, 6, 6, 255))
    dark.putalpha(outline)
    drop_shadow(img, dark, 0.8 * S, 0.8 * S, S * 0.5, alpha=150)
    img.alpha_composite(dark)
    img.alpha_composite(material(arrows, (214, 40, 34), 20, grime=0.25, chips=0.35, edge=0.8, outline=0.0))
    return vignette(img, inset=1, blur=1.0)


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    save(draw(True), root, "SCPageMore")
    save(draw(False), root, "SCPageBack")


if __name__ == "__main__":
    main()
