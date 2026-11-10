"""Shared painting helpers for the command-bar button icons (make-*-button.py).

Each vehicle part is drawn as a mask, then painted with `material`: lighting from the top
left, lit and shadowed edges, a dark outline, camouflage blotches, mud and dust that gather
low on the part, chipped paint and fine grain. Layering many small parts this way gives
a weathered, rendered look rather than flat shapes.
"""

import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

S = 8                       # drawing scale: shapes are given in button pixels and drawn at 8x
W, H = 60, 48               # button size in game pixels
WS, HS = W * S, H * S
OUT = 4                     # texels per button pixel in the saved texture (240x192 in 256x256)


def p(x, y):
    return (x * S, y * S)


def pts(points):
    return [p(x, y) for x, y in points]


def noise(scale, amount, seed, size=(WS, HS)):
    """Soft grey noise centred on 128; `scale` is the blob size in drawing pixels."""
    r = random.Random(seed)
    small = Image.new("L", (max(1, size[0] // scale), max(1, size[1] // scale)))
    small.putdata([max(0, min(255, 128 + int(r.uniform(-amount, amount)))) for _ in range(small.width * small.height)])
    return small.resize(size, Image.BICUBIC)


def threshold(img, level, soft=12):
    """0..255 mask of where the noise is above `level`, with a soft edge."""
    return img.point(lambda v: max(0, min(255, int((v - level) * 255 / max(1, soft)))))


def mix(a, b, mask):
    return Image.composite(b, a, mask)


def mask_of(draw_fn):
    m = Image.new("L", (WS, HS), 0)
    draw_fn(ImageDraw.Draw(m))
    return m


def material(mask, base, seed, grime=0.5, camo=None, chips=0.3, edge=1.0, outline=1.0):
    """Paints the area of `mask` and returns an RGBA layer."""
    box = mask.getbbox()
    if box is None:
        return Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    out = Image.new("RGB", (WS, HS), base)

    # light from the top left: darker toward the bottom right of the part
    grad = Image.new("L", (WS, HS), 0)
    g = Image.linear_gradient("L").resize((max(1, x1 - x0), max(1, y1 - y0)))
    grad.paste(g, (x0, y0))
    dark = tuple(int(c * 0.55) for c in base)
    out = mix(out, Image.new("RGB", (WS, HS), dark), grad.point(lambda v: int(v * 0.55)))

    # camouflage blotches
    if camo:
        blot = threshold(noise(14 * S, 90, seed + 1), 150, 30)
        out = mix(out, Image.new("RGB", (WS, HS), camo), blot.point(lambda v: int(v * 0.75)))

    # paint variation and grain
    out = ImageChops.add(out, noise(2 * S, 18, seed + 2).convert("RGB"), offset=-128)
    out = ImageChops.add(out, noise(3, 14, seed + 3).convert("RGB"), offset=-128)

    # mud and dust, heavier low down
    if grime > 0:
        dirt = threshold(noise(S, 110, seed + 4), 140, 40)
        low = grad.point(lambda v: int(min(255, v * 1.4)))
        dirt = ImageChops.multiply(dirt, low).point(lambda v: int(v * grime))
        out = mix(out, Image.new("RGB", (WS, HS), (112, 90, 60)), dirt)
        dust = ImageChops.multiply(threshold(noise(4 * S, 70, seed + 5), 128, 60), low).point(lambda v: int(v * grime * 0.6))
        out = mix(out, Image.new("RGB", (WS, HS), (176, 150, 108)), dust)

    # chipped paint: small bare-metal flecks
    if chips > 0:
        chip = threshold(noise(4, 120, seed + 6), 222, 10).point(lambda v: int(v * chips))
        out = mix(out, Image.new("RGB", (WS, HS), (58, 56, 50)), chip)

    # lit edges (top left) and shadowed edges (bottom right)
    d = int(1.2 * S)
    lit = ImageChops.subtract(mask, ImageChops.offset(mask, d, d)).filter(ImageFilter.GaussianBlur(S * 0.3))
    shade = ImageChops.subtract(mask, ImageChops.offset(mask, -d, -d)).filter(ImageFilter.GaussianBlur(S * 0.3))
    light = tuple(min(255, int(c * 1.45 + 20)) for c in base)
    out = mix(out, Image.new("RGB", (WS, HS), light), lit.point(lambda v: int(v * 0.7 * edge)))
    out = mix(out, Image.new("RGB", (WS, HS), (24, 22, 16)), shade.point(lambda v: int(v * 0.5 * edge)))

    # outline
    if outline > 0:
        inner = mask.filter(ImageFilter.MinFilter(5))
        ring = ImageChops.subtract(mask, inner).point(lambda v: int(v * 0.85 * outline))
        out = mix(out, Image.new("RGB", (WS, HS), (18, 18, 12)), ring)

    layer = out.convert("RGBA")
    layer.putalpha(mask)
    return layer


def paint(target, draw_fn, base, seed, **kw):
    target.alpha_composite(material(mask_of(draw_fn), base, seed, **kw))


def lines(target, segments, color, width):
    d = ImageDraw.Draw(target)
    for a, b in segments:
        d.line([p(*a), p(*b)], fill=color, width=max(1, int(width * S)))


def drop_shadow(target, layer, dx, dy, blur, alpha=140):
    sh = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    sh.paste((26, 18, 8, alpha), (0, 0), layer.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    target.alpha_composite(sh, (int(dx), int(dy)))


def vignette(img, inset=2, blur=1.5):
    vig = Image.new("L", (WS, HS), 0)
    ImageDraw.Draw(vig).rectangle([p(inset, inset), p(W - inset, H - inset)], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(S * blur))
    return Image.composite(img, Image.new("RGBA", (WS, HS), (30, 24, 16, 255)), vig)


def save(img, root, name):
    icon = img.resize((W * OUT, H * OUT), Image.LANCZOS)
    page = Image.new("RGBA", (64 * OUT, 64 * OUT), (0, 0, 0, 0))
    page.paste(icon, (0, 0))
    target = root / "resources" / "shared-control" / "Art" / "Textures" / (name + ".tga")
    target.parent.mkdir(parents=True, exist_ok=True)
    page.save(target)
    icon.save(target.with_name(name + "-preview.png"))
    print("Wrote", target)
