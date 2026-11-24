"""Builds the run-over mouse cursor, SCCRunOver.ani.

A tank track rolls up onto a wooden crate and flattens it, red impact lines bursting out
underneath. Like the game's own cursors it is 32x32 pixel art with a dark outline and the
hotspot in the middle; the only red is in the details (the road-wheel hubs and the impact
lines), so it is not mistaken for the red attack cursor. The frames are 32-bit cursors
(LoadCursorFromFile reads them on every supported Windows).

    python scripts/make-run-over-cursor.py [--preview <folder>]

Writes resources/shared-control/Cursors/SCCRunOver.ani. With --preview, also writes the
frames enlarged and an animated GIF to that folder.
"""

import math
import pathlib
import struct
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

U = 8                      # drawing scale: shapes are given in cursor pixels
N = 32                     # cursor size
HOT = (15, 15)             # hotspot, as in the game's move cursor
INK = (14, 14, 12, 255)
RED = (232, 40, 28, 255)   # like the run-over button
TREAD = (46, 44, 40, 255)
WHEEL = (150, 148, 136, 255)
CRATE = (204, 146, 72, 255)
CRATE_TOP = (232, 186, 112, 255)
CRATE_SIDE = (156, 104, 50, 255)
PLANK = (112, 70, 30, 255)

# One row per frame: track centre x, centre y, tilt (degrees, nose up), crate squash
# (0 whole .. 1 flat), impact lines, and how long the frame shows (1/60 s).
FRAMES = [
    (5.0, 17.0, 0, 0.0, False, 9),
    (8.5, 15.0, -14, 0.0, False, 9),
    (11.0, 12.0, -24, 0.35, False, 9),
    (14.0, 13.0, -10, 0.7, False, 9),
    (16.0, 14.5, 0, 1.0, True, 36),
]
GROUND = 21                # the crate stands on this row, just below the hotspot


def P(x, y):
    return (x * U, y * U)


def poly(d, points, fill):
    d.polygon([P(x, y) for x, y in points], fill=fill)


def canvas():
    return Image.new("RGBA", (N * U, N * U), (0, 0, 0, 0))


def finish(img):
    """Shrinks a drawing to 32x32 with hard edges and a 1-pixel dark outline, like the game's cursors."""
    small = img.resize((N, N), Image.LANCZOS)
    alpha = small.split()[3].point(lambda a: 255 if a >= 100 else 0)
    small.putalpha(alpha)
    ring = ImageChops.subtract(alpha.filter(ImageFilter.MaxFilter(3)), alpha)
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    out.paste(INK, (0, 0), ring)
    out.alpha_composite(small)
    return out


def crate(d, cx, base, squash):
    """A wooden crate standing on y=base, centred on cx. squash 0 = whole, 1 = flat."""
    h = 10 * (1 - squash) + 2.2 * squash
    w = 11 + 8 * squash
    depth = 3 * (1 - squash) + 1 * squash
    x0, x1 = cx - w / 2 - depth / 2, cx + w / 2 - depth / 2
    top = base - h
    poly(d, [(x0, top), (x0 + depth, top - depth), (x1 + depth, top - depth), (x1, top)], CRATE_TOP)
    poly(d, [(x1, top), (x1 + depth, top - depth), (x1 + depth, base - depth), (x1, base)], CRATE_SIDE)
    poly(d, [(x0, top), (x1, top), (x1, base), (x0, base)], CRATE)
    lw = int(0.9 * U)
    if squash < 0.5:
        d.line([P(x0 + 0.6, top + 0.6), P(x1 - 0.6, base - 0.6)], fill=PLANK, width=lw)      # cross brace
        d.line([P(x0 + 0.6, base - 0.6), P(x1 - 0.6, top + 0.6)], fill=PLANK, width=lw)
        d.rectangle([P(x0, top), P(x1, base)], outline=PLANK, width=lw)
    else:
        d.line([P(x0, top + h / 2), P(x1, top + h / 2)], fill=PLANK, width=lw)
        for sx, dx in ((x0, -1), (x1 + depth, 1)):                                           # splinters
            d.line([P(sx, base - 1), P(sx + 3.5 * dx, base - 3.2)], fill=CRATE, width=int(1.3 * U))
            d.line([P(sx, base - 0.5), P(sx + 2.5 * dx, base + 0.2)], fill=CRATE_TOP, width=int(1.1 * U))


def impact(d, cx, y, size=1.15):
    """Red impact lines bursting out from under the track."""
    for ang in (-160, -125, -55, -20):
        a = math.radians(ang)
        r0, r1 = 7 * size, 11 * size
        d.line([P(cx + math.cos(a) * r0, y + math.sin(a) * r0), P(cx + math.cos(a) * r1, y + math.sin(a) * r1)],
               fill=RED, width=int(1.6 * U))


def track(width=21, height=8.5):
    """A track loop seen from the side, with four road wheels, on its own layer, centred at (16, 16)."""
    layer = canvas()
    d = ImageDraw.Draw(layer)
    cx, cy = 16, 16
    x0, x1, y0, y1 = cx - width / 2, cx + width / 2, cy - height / 2, cy + height / 2
    d.rounded_rectangle([P(x0, y0), P(x1, y1)], radius=int(height / 2 * U), fill=TREAD)
    for k in range(int(width) + 2):                                                           # tread teeth
        x = x0 + 1.5 + k * 1.0
        if x < x1 - 1.5:
            d.rectangle([P(x, y0 - 0.9), P(x + 0.5, y0)], fill=TREAD)
            d.rectangle([P(x, y1), P(x + 0.5, y1 + 0.9)], fill=TREAD)
    r = height / 2 - 1.3
    for k in range(4):
        wx = x0 + height / 2 + k * (width - height) / 3
        d.ellipse([P(wx - r, cy - r), P(wx + r, cy + r)], fill=WHEEL)
        d.ellipse([P(wx - r * 0.4, cy - r * 0.4), P(wx + r * 0.4, cy + r * 0.4)], fill=RED)  # red hubs
    return layer


def frame(tx, ty, tilt, squash, burst):
    img = canvas()
    d = ImageDraw.Draw(img)
    crate(d, 18 - 2 * squash, GROUND, squash)
    t = track().rotate(-tilt, center=P(16, 16), resample=Image.BICUBIC)
    img.alpha_composite(t, (int((tx - 16) * U), int((ty - 16) * U)))
    if burst:
        impact(ImageDraw.Draw(img), 16, GROUND - 2)
    return finish(img)


# --- file writing ----------------------------------------------------------------------------

def cur_bytes(img, hotspot):
    """One 32x32 32-bit cursor (.cur) with an AND mask."""
    w, h = img.size
    px = img.load()
    xor = bytearray()
    for y in range(h - 1, -1, -1):                       # bottom-up rows, BGRA
        for x in range(w):
            r, g, b, a = px[x, y]
            xor += bytes((b, g, r, a))
    row = ((w + 31) // 32) * 4
    mask = bytearray()
    for y in range(h - 1, -1, -1):
        bits = bytearray(row)
        for x in range(w):
            if px[x, y][3] == 0:
                bits[x // 8] |= 0x80 >> (x % 8)          # 1 = transparent
        mask += bits
    header = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(xor) + len(mask), 0, 0, 0, 0)
    image = header + xor + mask
    directory = struct.pack("<HHH", 0, 2, 1)
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, hotspot[0], hotspot[1], len(image), 6 + 16)
    return directory + entry + image


def chunk(tag, data):
    return tag + struct.pack("<I", len(data)) + data + (b"\0" if len(data) & 1 else b"")


def ani_bytes(images, rates, hotspot):
    n = len(images)
    anih = struct.pack("<9I", 36, n, n, 0, 0, 0, 0, rates[0], 1 | 2)   # AF_ICON | AF_SEQUENCE
    body = chunk(b"anih", anih)
    body += chunk(b"rate", struct.pack(f"<{n}I", *rates))
    body += chunk(b"seq ", struct.pack(f"<{n}I", *range(n)))
    frames = b"".join(chunk(b"icon", cur_bytes(img, hotspot)) for img in images)
    body += chunk(b"LIST", b"fram" + frames)
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"ACON" + body


def main():
    images = [frame(*row[:5]) for row in FRAMES]
    rates = [row[5] for row in FRAMES]
    root = pathlib.Path(__file__).resolve().parent.parent
    target = root / "resources" / "shared-control" / "Cursors" / "SCCRunOver.ani"
    target.parent.mkdir(parents=True, exist_ok=True)
    data = ani_bytes(images, rates, HOT)
    target.write_bytes(data)
    print(f"Wrote {target} ({len(data)} bytes, {len(images)} frames)")
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        out = pathlib.Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        z = 6
        strip = Image.new("RGBA", (len(images) * (N * z + 8), N * z), (0, 0, 0, 255))
        for i, img in enumerate(images):
            strip.alpha_composite(img.resize((N * z, N * z), Image.NEAREST), (i * (N * z + 8), 0))
        strip.save(out / "run-over-cursor-frames.png")
        gif = [Image.new("RGBA", (N * z, N * z), (110, 102, 76, 255)) for _ in images]
        for g, img in zip(gif, images):
            g.alpha_composite(img.resize((N * z, N * z), Image.NEAREST))
        gif = [g.convert("P", palette=Image.ADAPTIVE) for g in gif]
        gif[0].save(out / "run-over-cursor.gif", save_all=True, append_images=gif[1:],
                    duration=[r * 1000 // 60 for r in rates], loop=0)
        print("Wrote previews to", out)


if __name__ == "__main__":
    main()
