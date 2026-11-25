"""Builds the repair-and-return command-bar button, SCRepairReturn.tga.

The single-barrel tank of the run-over button (generic, not a model from the game), seen
from its front quarter and filling the button, a little scorched, with a steel wrench laid
over it and a green arrow curving out and back round it: get fixed, then come back.

    python scripts/make-repair-return-button.py [--preview <folder>]

Writes resources/shared-control/Art/Textures/SCRepairReturn.tga and a preview PNG beside it.
With --preview, also writes the icon big and at in-game size to that folder.
"""

import importlib.util
import math
import pathlib
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from button_paint import H, HS, OUT, S, W, WS, drop_shadow, material, p, save, vignette

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("run_over_button", HERE / "make-run-over-button.py")
ro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ro)

ro.PITCH = 0.0                       # standing level on the ground
ro.TURRET_YAW = -12                  # gun forward and a little away, clear above the hull
ro.BARRELS = ((0.0, 0.18),)          # one gun

CAM_EYE = (12.0, 13.5, 7.0)
CAM_TARGET = (4.6, 0.0, 1.3)
CAM_ZOOM = 108.0
CAM_CENTER = (26.5, 30.5)

STEEL_LIGHT = (176, 180, 186)
GREEN = (74, 206, 92)
INK = (16, 16, 12, 255)

WRENCH = (25.5, 19.0, 28.0, 3.8, -24)          # centre x, y, length, handle width, angle
ARROW = (29.5, 27.0, 26.5, 16.5, 168, 398, 2.4)  # centre x, y, radius x, y, from, to (degrees), width


def rotate_pts(points, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in points]


def wrench_mask(cx, cy, length, width, angle):
    """A double open-end wrench centred at (cx, cy), in button pixels."""
    a = math.radians(angle)
    m = Image.new("L", (WS, HS), 0)
    d = ImageDraw.Draw(m)
    half, hw = length / 2, width / 2
    d.polygon([p(*q) for q in rotate_pts([(-half, -hw), (half, -hw), (half, hw), (-half, hw)], cx, cy, a)], fill=255)
    for sign, size in ((1, 1.0), (-1, 0.85)):
        r = width * 1.45 * size
        hx, hy = rotate_pts([(sign * half, 0)], cx, cy, a)[0]
        d.ellipse([p(hx - r, hy - r), p(hx + r, hy + r)], fill=255)
        # the jaw: a slot opening outward, turned a little off the handle line
        ja = a + math.radians(15 * sign) + (0 if sign > 0 else math.pi)
        slot = rotate_pts([(r * 0.05, -r * 0.42), (r * 1.4, -r * 0.42), (r * 1.4, r * 0.42), (r * 0.05, r * 0.42)], hx, hy, ja)
        d.polygon([p(*q) for q in slot], fill=0)
        d.ellipse([p(hx - r * 0.45, hy - r * 0.45), p(hx + r * 0.45, hy + r * 0.45)], fill=0)
    return m


def wrench(img, cx, cy, length, width, angle):
    mask = wrench_mask(cx, cy, length, width, angle)
    layer = material(mask, STEEL_LIGHT, 900, grime=0.08, chips=0.05, edge=1.3, outline=1.4)
    a = math.radians(angle)
    shine = Image.new("L", (WS, HS), 0)
    q = rotate_pts([(-length * 0.32, -width * 0.18), (length * 0.32, -width * 0.18)], cx, cy, a)
    ImageDraw.Draw(shine).line([p(*q[0]), p(*q[1])], fill=200, width=int(width * 0.22 * S))
    shine = ImageChops.multiply(shine.filter(ImageFilter.GaussianBlur(S * 0.3)), mask)
    hi = Image.new("RGBA", (WS, HS), (246, 248, 252, 255))
    hi.putalpha(shine)
    halo = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    halo.paste(INK, (0, 0), mask.filter(ImageFilter.MaxFilter(9)))
    drop_shadow(img, layer, 0.8 * S, 1.3 * S, S * 0.7, alpha=170)       # it lies on the tank
    img.alpha_composite(halo)
    img.alpha_composite(layer)
    img.alpha_composite(hi)


def return_arrow(img, cx, cy, rx, ry, start, end, width):
    """A green arrow along an ellipse from `start` to `end` degrees, head at the end, as a layer."""
    def at(deg):
        a = math.radians(deg)
        return (cx + rx * math.cos(a), cy + ry * math.sin(a))

    steps = 48
    path = [at(start + (end - start) * i / steps) for i in range(steps + 1)]
    ex, ey = path[-1]
    px, py = path[-4]
    ang = math.atan2(ey - py, ex - px)
    head = [(ex + math.cos(ang) * width * 1.7, ey + math.sin(ang) * width * 1.7),
            (ex + math.cos(ang + 2.2) * width * 1.6, ey + math.sin(ang + 2.2) * width * 1.6),
            (ex + math.cos(ang - 2.2) * width * 1.6, ey + math.sin(ang - 2.2) * width * 1.6)]
    hx, hy = sum(q[0] for q in head) / 3, sum(q[1] for q in head) / 3
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for grow, col in ((1.3, INK), (0.0, GREEN + (255,))):
        d.line([p(*q) for q in path], fill=col, width=int((width + grow) * S), joint="curve")
        k = 1.0 + grow * 0.3
        d.polygon([p(hx + (q[0] - hx) * k, hy + (q[1] - hy) * k) for q in head], fill=col)
    # a lighter line along the top of the arrow so it reads as a band, not a flat stroke
    d.line([p(q[0], q[1] - width * 0.22) for q in path[2:-3]], fill=(170, 246, 170, 255), width=max(1, int(width * 0.25 * S)), joint="curve")
    return layer


def arrow_half(layer, cy, far):
    """The far half of the arrow (above its centre line) goes behind the tank, the near half in front."""
    half = Image.new("L", (WS, HS), 0)
    box = [0, 0, WS, int(cy * S)] if far else [0, int(cy * S), WS, HS]
    ImageDraw.Draw(half).rectangle(box, fill=255)
    part = layer.copy()
    part.putalpha(ImageChops.multiply(layer.split()[3], half))
    return part


def scorch(img, cam, spots):
    """Burn marks on the hull: this tank needs fixing."""
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (x, y, z), r in spots:
        sx, sy = cam.project((x, y, z))
        d.ellipse([p(sx - r, sy - r * 0.7), p(sx + r, sy + r * 0.7)], fill=(22, 18, 12, 170))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(S * 0.5)))


def scene():
    cam = ro.Camera(eye=CAM_EYE, target=CAM_TARGET, zoom=CAM_ZOOM, center=CAM_CENTER)
    img = ro.ground()
    sh = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    foot = [(-0.6, -2.2, 0), (8.6, -2.2, 0), (8.6, 2.3, 0), (-0.6, 2.3, 0)]
    ImageDraw.Draw(sh).polygon([p(*cam.project(q)) for q in foot], fill=(36, 26, 14, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S * 1.2)))
    arrow = return_arrow(img, *ARROW)
    img.alpha_composite(arrow_half(arrow, ARROW[1], far=True))
    tank = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    ro.tank(tank, cam)
    img.alpha_composite(tank)
    scorch(img, cam, [((1.2, 1.2, 2.1), 1.7), ((2.4, 1.95, 1.5), 1.2), ((6.9, 1.0, 1.8), 1.1)])
    img.alpha_composite(arrow_half(arrow, ARROW[1], far=False))
    wrench(img, *WRENCH)
    return vignette(img)


def preview(img, out):
    try:
        font = ImageFont.truetype("segoeuib.ttf", 26)
        small = ImageFont.truetype("segoeui.ttf", 18)
    except OSError:
        font = small = ImageFont.load_default()
    pad = 30
    bw, bh = W * OUT, H * OUT
    page = Image.new("RGBA", (pad * 2 + bw, 80 + bh + 40 + H * 2 + 30), (24, 28, 22, 255))
    d = ImageDraw.Draw(page)
    d.text((pad, 28), "Repair and Return", fill=(237, 242, 233), font=font)
    page.alpha_composite(img.resize((bw, bh), Image.LANCZOS), (pad, 80))
    d.text((pad, 80 + bh + 12), "in game, actual size:", fill=(171, 183, 166), font=small)
    page.alpha_composite(img.resize((W * 2, H * 2), Image.LANCZOS), (pad, 80 + bh + 40))
    page.alpha_composite(img.resize((W, H), Image.LANCZOS), (pad + W * 2 + 20, 80 + bh + 40))
    page.save(out / "repair-return-button.png")
    print("Wrote", out / "repair-return-button.png")


def main():
    img = scene()
    save(img, HERE.parent, "SCRepairReturn")
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        out = pathlib.Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        preview(img, out)


if __name__ == "__main__":
    main()
