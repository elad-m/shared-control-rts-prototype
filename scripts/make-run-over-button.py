"""Builds the run-over command-bar button, SCRunOver.tga.

A heavy twin-barrel tank (generic, not a model from the game), seen low from its front
quarter, has its front up on a smaller enemy tank it is crushing, sparks flying; a soldier
in field colours falls beside its track. The soldier and the crushed tank are outlined in
red so the victims stand out. The scene is built from simple 3D solids, projected with a
perspective camera, painted with the button_paint materials and framed tight on the crash.

    python scripts/make-run-over-button.py [--preview <folder>]

Writes resources/shared-control/Art/Textures/SCRunOver.tga and a preview PNG beside it.
With --preview, also writes a sheet comparing red and blue outlines to that folder.
"""

import math
import pathlib
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from button_paint import H, HS, S, W, WS, lines, noise, p, paint, pts, save, vignette, OUT

OLIVE = (104, 106, 76)
OLIVE_DARK = (74, 76, 54)
CAMO = (126, 114, 80)
RUBBER = (44, 42, 38)
STEEL = (70, 68, 62)
ENEMY = (128, 124, 114)     # grey, apart from the olive tank and the dirt
ENEMY_DARK = (78, 76, 70)
BLUE = (40, 110, 230)
RED = (226, 44, 32)
MARK = RED                  # outline that picks out the victims: the soldier and the crushed tank


# --- tiny 3D -----------------------------------------------------------------------------

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    length = math.sqrt(dot(a, a)) or 1.0
    return (a[0] / length, a[1] / length, a[2] / length)


class Camera:
    def __init__(self, eye, target, zoom, center, mirror=True):
        self.mirror = mirror
        self.eye = eye
        self.f = norm(sub(target, eye))
        self.r = norm(cross(self.f, (0, 0, 1)))
        self.u = cross(self.r, self.f)
        self.zoom = zoom
        self.center = center

    def to_view(self, q):
        v = sub(q, self.eye)
        return (dot(v, self.r), dot(v, self.u), dot(v, self.f))

    def project(self, q):
        x, y, z = self.to_view(q)
        sx = self.center[0] + self.zoom * x / z
        # mirrored so the tank drives toward the right, as in the reference photo
        return (W - sx if self.mirror else sx, self.center[1] - self.zoom * y / z)

    def depth(self, q):
        return self.to_view(q)[2]


def prism(profile, y0, y1):
    """Faces of a solid: an X-Z profile extruded along Y from y0 to y1."""
    faces = [[(x, y1, z) for x, z in profile], [(x, y0, z) for x, z in reversed(profile)]]
    n = len(profile)
    for i in range(n):
        (xa, za), (xb, zb) = profile[i], profile[(i + 1) % n]
        faces.append([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)])
    return faces


def frustum(x0, x1, y0, y1, z0, inset, z1, front_inset=0.0):
    """A box whose top is smaller than its bottom (a turret)."""
    b = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    t = [(x0 + inset, y0 + inset, z1), (x1 - inset - front_inset, y0 + inset, z1),
         (x1 - inset - front_inset, y1 - inset, z1), (x0 + inset, y1 - inset, z1)]
    faces = [b[::-1], t]
    for i in range(4):
        j = (i + 1) % 4
        faces.append([b[i], b[j], t[j], t[i]])
    return faces


def cylinder(a, b, radius, sides=8):
    axis = norm(sub(b, a))
    helper = (0, 0, 1) if abs(axis[2]) < 0.9 else (1, 0, 0)
    e1 = norm(cross(axis, helper))
    e2 = cross(axis, e1)
    ring = [(math.cos(2 * math.pi * k / sides), math.sin(2 * math.pi * k / sides)) for k in range(sides)]
    ra = [tuple(a[i] + radius * (c * e1[i] + s * e2[i]) for i in range(3)) for c, s in ring]
    rb = [tuple(b[i] + radius * (c * e1[i] + s * e2[i]) for i in range(3)) for c, s in ring]
    faces = [ra[::-1], rb]
    for k in range(sides):
        j = (k + 1) % sides
        faces.append([ra[k], ra[j], rb[j], rb[k]])
    return faces


def disc(center, radius, sides=16):
    """A flat circle facing +Y (a wheel on the left side)."""
    cx, cy, cz = center
    return [(cx + radius * math.cos(2 * math.pi * k / sides), cy, cz + radius * math.sin(2 * math.pi * k / sides)) for k in range(sides)]


def transform(points, pitch=0.0, yaw=0.0, pivot=(0, 0, 0), move=(0, 0, 0)):
    out = []
    cp, sp = math.cos(pitch), math.sin(pitch)
    cyw, syw = math.cos(yaw), math.sin(yaw)
    for x, y, z in points:
        x, y, z = x - pivot[0], y - pivot[1], z - pivot[2]
        x, y = x * cyw - y * syw, x * syw + y * cyw          # yaw about Z
        x, z = x * cp - z * sp, x * sp + z * cp              # nose up about Y
        out.append((x + pivot[0] + move[0], y + pivot[1] + move[1], z + pivot[2] + move[2]))
    return out


LIGHT = norm((-0.25, 0.6, 0.8))     # world direction toward the light: camera side, high


def solid(layer, cam, faces, base, seed, centroid=None, **kw):
    """Paints the camera-facing faces of a convex solid, far faces first."""
    if centroid is None:
        allp = [q for f in faces for q in f]
        centroid = tuple(sum(q[i] for q in allp) / len(allp) for i in range(3))
    visible = []
    for f in faces:
        n = norm(cross(sub(f[1], f[0]), sub(f[2], f[0])))
        mid = tuple(sum(q[i] for q in f) / len(f) for i in range(3))
        if dot(n, sub(mid, centroid)) < 0:
            n = (-n[0], -n[1], -n[2])
        if dot(n, sub(cam.eye, mid)) <= 0:
            continue
        visible.append((cam.depth(mid), f, n))
    visible.sort(key=lambda t: -t[0])
    for k, (_, f, n) in enumerate(visible):
        shade = 0.5 + 0.62 * max(0.0, dot(n, LIGHT))
        color = tuple(max(0, min(255, int(c * shade))) for c in base)
        poly = [cam.project(q) for q in f]
        paint(layer, lambda d, poly=poly: d.polygon(pts(poly), fill=255), color, seed + k, **kw)
        record_depth(layer, cam, poly, f[0], n)


DEPTHS = {}      # id(layer) -> per-pixel distance of the nearest face painted on it


def record_depth(layer, cam, poly, on_plane, n):
    mask = Image.new("L", (WS, HS), 0)
    ImageDraw.Draw(mask).polygon(pts(poly), fill=255)
    inside = np.asarray(mask) > 0
    if not inside.any():
        return
    ys, xs = np.nonzero(inside)
    sx = xs / S
    sx = W - sx if cam.mirror else sx
    rx = (sx - cam.center[0]) / cam.zoom
    ry = -(ys / S - cam.center[1]) / cam.zoom
    p0 = cam.to_view(on_plane)
    nv = (dot(n, cam.r), dot(n, cam.u), dot(n, cam.f))
    denom = nv[0] * rx + nv[1] * ry + nv[2]
    z = dot(nv, p0) / np.where(np.abs(denom) < 1e-6, 1e-6, denom)
    depth = DEPTHS.setdefault(id(layer), np.full((HS, WS), np.inf))
    depth[ys, xs] = np.minimum(depth[ys, xs], z)


def composite_by_depth(img, a, b):
    """Puts layers a and b on img, each pixel taken from whichever is nearer the camera."""
    da = DEPTHS.get(id(a), np.full((HS, WS), np.inf))
    db = DEPTHS.get(id(b), np.full((HS, WS), np.inf))
    b_front = Image.fromarray(((db < da) * 255).astype(np.uint8))
    a_alpha, b_alpha = a.split()[3], b.split()[3]
    a_cut = a.copy()
    a_cut.putalpha(ImageChops.subtract(a_alpha, ImageChops.multiply(b_alpha, b_front)))
    b_cut = b.copy()
    b_cut.putalpha(ImageChops.multiply(b_alpha, ImageChops.invert(ImageChops.multiply(a_alpha, ImageChops.invert(b_front)))))
    img.alpha_composite(a_cut)
    img.alpha_composite(b_cut)
    return b_cut


# --- scene -------------------------------------------------------------------------------

PITCH = math.radians(9)               # nose up: the front of the tracks rests on the enemy tank
PIVOT = (0.0, 0.0, 0.0)              # rear of the tracks stays on the ground


def T(points):
    return transform(points, pitch=PITCH, pivot=PIVOT)


def tank(layer, cam):
    # the far track, then the deck (its underside shows from this low camera, so it must go
    # behind the near track), then the near track
    track = [(-0.25, 0.7), (0.45, 0.0), (7.0, 0.0), (7.8, 0.72), (7.65, 1.12), (0.0, 1.12)]
    solid(layer, cam, [T(f) for f in prism(track, -1.9, -1.15)], RUBBER, 100, grime=0.9, chips=0)
    # upper hull: wide deck over both tracks, long sloped front plate
    deck = [(-0.3, 1.1), (7.75, 1.1), (8.35, 1.42), (6.4, 2.05), (-0.25, 2.05)]
    solid(layer, cam, [T(f) for f in prism(deck, -1.95, 1.95)], OLIVE, 200, grime=0.7, camo=CAMO)
    solid(layer, cam, [T(f) for f in prism(track, 1.15, 1.9)], RUBBER, 120, grime=0.9, chips=0)
    # road wheels, front idler and rear sprocket on the near (left) side, with hubs
    wheels = [(0.9 + i * 1.12, 0.52, 0.48) for i in range(6)] + [(7.22, 0.62, 0.36), (0.02, 0.66, 0.38)]
    for i, (x, z, r) in enumerate(wheels):
        rim = T(disc((x, 1.92, z), r))
        hub = T(disc((x, 1.93, z), r * 0.38, sides=10))
        paint(layer, lambda d, q=rim: d.polygon(pts([cam.project(v) for v in q]), fill=255), (100, 98, 84), 140 + i, grime=0.7, chips=0.2)
        paint(layer, lambda d, q=hub: d.polygon(pts([cam.project(v) for v in q]), fill=255), (56, 54, 46), 150 + i, grime=0.3, edge=0.4)
    # tread grousers across the front slope of the near track (the top run is under the deck)
    segs = []
    for k in range(14):
        t = k / 13.0
        a = (7.0 + 0.8 * t, 0.72 * t)
        segs.append((a, 1.15, 1.9))
    tread = []
    for (x, z), y0, y1 in segs:
        q0, q1 = T([(x, y0, z), (x, y1, z)])
        tread.append((cam.project(q0), cam.project(q1)))
    lines(layer, tread, (24, 22, 18, 255), 0.28)
    # headlights on the front plate
    for y in (1.45, -1.45):
        c = T([(8.05, y, 1.52)])[0]
        sx, sy = cam.project(c)
        ImageDraw.Draw(layer).ellipse([p(sx - 0.9, sy - 0.7), p(sx + 0.9, sy + 0.7)], fill=(30, 30, 24, 255))
        ImageDraw.Draw(layer).ellipse([p(sx - 0.5, sy - 0.45), p(sx + 0.3, sy + 0.25)], fill=(200, 196, 160, 255))
    # turret, turned toward the left like the reference photo
    yaw = math.radians(TURRET_YAW)
    tc = (3.6, 0.0, 2.05)
    tur = frustum(-2.0, 2.3, -1.55, 1.55, 0.0, 0.35, 1.05, front_inset=0.5)
    tur = [transform(f, yaw=yaw, move=tc) for f in tur]
    tur = [T(f) for f in tur]
    # barrels go first so the turret front covers their roots
    for dy, r in BARRELS:
        a = T(transform([(1.6, dy, 0.62)], yaw=yaw, move=tc))[0]
        b = T(transform([(8.5, dy, 0.62)], yaw=yaw, move=tc))[0]
        m = T(transform([(7.4, dy, 0.62)], yaw=yaw, move=tc))[0]
        solid(layer, cam, cylinder(a, b, r), OLIVE_DARK, 300 + int(dy * 10), grime=0.1, outline=0.6)
        solid(layer, cam, cylinder(m, b, r * 1.5), STEEL, 310 + int(dy * 10), grime=0.1, outline=0.6)
    solid(layer, cam, tur, OLIVE, 320, grime=0.4, camo=CAMO)
    cupola = [T(transform(f, yaw=yaw, move=tc)) for f in frustum(-1.3, -0.3, -0.95, 0.05, 1.05, 0.1, 1.35)]
    solid(layer, cam, cupola, OLIVE_DARK, 340, grime=0.3)


def enemy_tank(layer, cam):
    """A smaller enemy tank under the heavy tank's front: hull crushed at the back, turret
    knocked loose and tipped, barrel bent."""
    y0, y1 = ENEMY_Y
    ym = (y0 + y1) / 2
    track = [(4.8, 0.24), (5.1, 0.0), (9.0, 0.0), (9.45, 0.34), (9.25, 0.58), (4.8, 0.54)]
    solid(layer, cam, prism(track, y0, y0 + 0.45), RUBBER, 500, grime=0.9, chips=0)
    # hull: whole at the front, pressed down where the heavy track sits on it
    hull = [(4.6, 0.46), (9.55, 0.46), (9.8, 0.76), (8.9, 1.16), (7.6, 1.16), (7.0, 0.92), (5.7, 0.62), (4.6, 0.54)]
    solid(layer, cam, prism(hull, y0 + 0.05, y1 - 0.05), ENEMY, 510, grime=0.8, chips=0.7, centroid=(7.6, ym, 0.75))
    solid(layer, cam, prism(track, y1 - 0.45, y1), RUBBER, 520, grime=0.9, chips=0)
    for i in range(5):
        x = 5.45 + i * 0.84
        rim = disc((x, y1 + 0.01, 0.27), 0.24, sides=12)
        paint(layer, lambda d, q=rim: d.polygon(pts([cam.project(v) for v in q]), fill=255), (92, 90, 80), 530 + i, grime=0.6, chips=0.2, edge=0.5)

    # turret knocked loose: shoved forward and to the far side, tipped, barrel bent
    def place(points):
        return transform(points, pitch=math.radians(-18), yaw=math.radians(-35), move=(8.5, ym - 0.35, 1.12))

    for a, b, r, seed in (((0.8, 0, 0.36), (2.0, 0, 0.36), 0.1, 540), ((2.0, 0, 0.36), (2.8, 0, -0.3), 0.095, 541)):
        solid(layer, cam, cylinder(*place([a, b]), r), ENEMY_DARK, seed, grime=0.2, outline=0.6)
    tur = [place(f) for f in frustum(-0.95, 1.05, -0.8, 0.8, 0.0, 0.18, 0.7, front_inset=0.25)]
    solid(layer, cam, tur, ENEMY, 550, grime=0.6, chips=0.6)
    # dents where the track bears down
    crease = [((6.0, y1, 0.66), (6.5, y1, 0.5)), ((6.9, y1, 0.9), (7.3, y1, 0.62)), ((5.6, y1 - 0.3, 0.62), (6.6, y1 - 0.9, 0.84))]
    lines(layer, [(cam.project(a), cam.project(b)) for a, b in crease], (40, 38, 34, 255), 0.35)


def soldier(layer, x, y, angle, scale):
    """A soldier in field uniform with helmet, boots, pack and rifle, outlined in MARK, feet at
    (x, y), facing left (toward the tank) and thrown backwards by `angle` degrees."""
    a = math.radians(angle)

    def rot(dx, dy):
        dx, dy = dx * scale, dy * scale
        return (x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a))

    d = ImageDraw.Draw(layer)

    def limb(p0, p1, w, c, grow):
        w = w + grow
        d.line([p(*rot(*p0)), p(*rot(*p1))], fill=c, width=max(1, int(w * S * scale)))
        for q in (p0, p1):
            cx, cy = rot(*q)
            r = w * scale / 2
            d.ellipse([p(cx - r, cy - r), p(cx + r, cy + r)], fill=c)

    def poly(points, c, grow):
        if grow:
            d.line([p(*rot(*q)) for q in points + points[:1]], fill=c, width=int(grow * S * scale), joint="curve")
        d.polygon([p(*rot(*q)) for q in points], fill=c)

    def ball(cx, cy, r, c, grow):
        cx, cy = rot(cx, cy)
        r = (r + grow / 2) * scale
        d.ellipse([p(cx - r, cy - r), p(cx + r, cy + r)], fill=c)

    ink = (16, 18, 22, 255)
    uniform = (128, 122, 82, 255)      # khaki jacket
    trousers = (104, 100, 68, 255)
    shade = (80, 78, 52, 255)          # far arm and leg
    pack = (74, 66, 46, 255)
    boot = (46, 36, 26, 255)
    skin = (204, 158, 118, 255)
    helmet = (70, 78, 54, 255)
    gun = (34, 34, 32, 255)

    def figure(g, outline=None):
        def c(col):
            return outline or col
        poly([(1.1, -8.9), (2.7, -8.6), (2.8, -5.6), (1.2, -5.9)], c(pack), g)            # backpack
        limb((1.0, -8.6), (3.6, -11.2), 1.15, c(shade), g)                                    # far arm
        limb((0.4, -5.0), (1.3, -2.6), 1.45, c(shade), g)                                     # far leg
        limb((1.3, -2.6), (1.9, -0.3), 1.3, c(shade), g)
        limb((1.9, -0.3), (2.9, -0.3), 1.1, c(boot), g)                                       # far boot
        poly([(-1.5, -5.4), (1.4, -5.4), (1.5, -9.0), (-1.4, -9.3)], c(uniform), g)          # jacket
        limb((-0.4, -5.0), (-1.4, -2.7), 1.5, c(trousers), g)                                 # near leg
        limb((-1.4, -2.7), (-1.6, -0.3), 1.35, c(trousers), g)
        limb((-1.6, -0.2), (-2.7, -0.2), 1.15, c(boot), g)                                    # near boot
        ball(-0.1, -10.4, 1.05, c(skin), g)                                                   # head
        limb((-0.9, -8.8), (-3.2, -11.4), 1.2, c(uniform), g)                                 # near arm, thrown up
        ball(-3.4, -11.7, 0.5, c(skin), g)                                                    # hands
        ball(3.8, -11.4, 0.48, c(skin), g)
        poly([(-1.55, -10.6), (-1.2, -11.6), (-0.2, -12.1), (0.9, -11.8), (1.4, -10.9), (1.7, -10.5)], c(helmet), g)
        limb((-5.4, -13.4), (-1.0, -10.1), 0.55, c(gun), g)                                   # rifle flying from his hand
        limb((-1.0, -10.1), (0.0, -9.6), 0.9, c(gun), g)                                      # its stock
        limb((-3.4, -12.0), (-3.0, -11.1), 0.45, c(gun), g)                                   # magazine

    figure(2.0, MARK + (255,))
    figure(0.75, ink)
    figure(0.0)
    # belt and a highlight down the jacket
    d.line([p(*rot(-1.5, -5.6)), p(*rot(1.45, -5.6))], fill=(20, 26, 40, 255), width=max(1, int(0.45 * S * scale)))
    d.line([p(*rot(-1.0, -6.0)), p(*rot(-0.9, -8.6))], fill=(176, 170, 120, 255), width=max(1, int(0.35 * S * scale)))


def sparks(img, x, y, rng, count=16):
    """Hot sparks and a puff of dark smoke where steel is being crushed."""
    layer = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(9):
        cx, cy = x + rng.uniform(-2.5, 3.5), y - rng.uniform(0, 5)
        r = rng.uniform(1.2, 2.4)
        g = rng.randint(40, 70)
        d.ellipse([p(cx - r, cy - r), p(cx + r, cy + r)], fill=(g, g, g - 4, rng.randint(70, 130)))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(S * 0.8)))
    d = ImageDraw.Draw(img)
    for _ in range(count):
        ang = rng.uniform(math.radians(200), math.radians(340))
        length = rng.uniform(1.6, 4.6)
        x1, y1 = x + math.cos(ang) * length, y + math.sin(ang) * length
        d.line([p(x, y), p(x1, y1)], fill=(255, 214, 120, 255), width=int(0.45 * S))
        d.ellipse([p(x1 - 0.4, y1 - 0.4), p(x1 + 0.4, y1 + 0.4)], fill=(255, 246, 200, 255))


def ground():
    img = Image.new("RGB", (WS, HS))
    d = ImageDraw.Draw(img)
    for y in range(HS):
        t = y / HS
        d.line([(0, y), (WS, y)], fill=(int(170 - 52 * t), int(146 - 46 * t), int(106 - 38 * t)))
    for scale, amount, seed in ((4 * S, 24, 1), (S, 16, 2), (3, 12, 3)):
        img = ImageChops.add(img, noise(scale, amount, seed).convert("RGB"), offset=-128)
    return img.convert("RGBA")


ENEMY_Y = (-0.4, 1.75)           # under the near half of the tank; its near track rides the enemy hull
SPARKS_AT = (6.4, 1.8, 0.8)
TURRET_YAW = -25                 # barrels over the enemy tank, slightly away from the camera
BARRELS = ((-0.42, 0.14), (0.42, 0.14))   # (sideways offset, radius) of each gun barrel: twin, like an Overlord
CAM_EYE = (13.5, 11.5, 0.5)      # low, off the front left of the tank (mirrored to front right)
CAM_TARGET = (6.5, 0.0, 1.4)
CAM_ZOOM = 125.0
CAM_CENTER = (24.5, 27.5)
SOLDIER_AT = (4.9, 2.7, 0.0)     # beside the near track, just behind the crushed tank
SOLDIER_TILT = 26
SOLDIER_HEIGHT = 1.7


def scene():
    cam = Camera(eye=CAM_EYE, target=CAM_TARGET, zoom=CAM_ZOOM, center=CAM_CENTER)
    img = ground()
    # ruts and the shadow under both tanks
    sh = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    foot = [(-0.5, -2.1, 0), (8.0, -2.1, 0), (13.0, -2.6, 0), (13.0, 0.0, 0), (8.6, 2.2, 0), (-0.5, 2.2, 0)]
    sd.polygon(pts([cam.project(q) for q in foot]), fill=(36, 26, 14, 170))
    for y in (1.5, -1.5):
        rut = [(-6, y - 0.4, 0), (0.5, y - 0.4, 0), (0.5, y + 0.4, 0), (-6, y + 0.4, 0)]
        sd.polygon(pts([cam.project(q) for q in rut]), fill=(80, 62, 40, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S * 1.2)))
    t = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    tank(t, cam)
    v = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    enemy_tank(v, cam)
    enemy_seen = composite_by_depth(img, t, v).split()[3]
    # the heavy tank's shadow falls on the enemy tank right under its track
    drop = ImageChops.offset(t.split()[3], 0, int(1.6 * S)).filter(ImageFilter.GaussianBlur(S * 0.8))
    on_enemy = ImageChops.multiply(drop, v.split()[3])
    on_enemy = ImageChops.subtract(on_enemy, t.split()[3]).point(lambda a: int(a * 0.55))
    shade = Image.new("RGBA", (WS, HS), (30, 26, 18, 255))
    shade.putalpha(on_enemy)
    img.alpha_composite(shade)
    # a MARK line just inside the edge of what shows of the crushed tank
    ring = ImageChops.subtract(enemy_seen, enemy_seen.filter(ImageFilter.MinFilter(11)))
    inside = Image.new("L", (WS, HS), 0)                  # no line where the frame cuts it off
    ImageDraw.Draw(inside).rectangle([8, 8, WS - 9, HS - 9], fill=255)
    ring = ImageChops.multiply(ring, inside)
    mark = Image.new("RGBA", (WS, HS), MARK + (255,))
    mark.putalpha(ring.filter(ImageFilter.GaussianBlur(S * 0.15)))
    img.alpha_composite(mark)
    # the soldier, just ahead of the near track, falling back as it reaches him
    fx, fy = cam.project(SOLDIER_AT)
    hx, hy = cam.project((SOLDIER_AT[0], SOLDIER_AT[1], SOLDIER_AT[2] + SOLDIER_HEIGHT))
    sparks(img, *cam.project(SPARKS_AT), random.Random(7))
    soldier(img, fx, fy, SOLDIER_TILT, (fy - hy) / 12.0)   # a man of SOLDIER_HEIGHT at that spot
    return vignette(img)


def main():
    global MARK
    save(scene(), pathlib.Path(__file__).resolve().parent.parent, "SCRunOver")
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        out = pathlib.Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        variants = []
        for name, color in (("red", RED), ("blue", BLUE)):
            MARK = color
            variants.append((name, scene()))
        MARK = RED
        sheet(out, variants)


def sheet(out, variants):
    """One column per variant: the icon big, then at in-game size (2x and 1x)."""
    try:
        font = ImageFont.truetype("segoeuib.ttf", 26)
        small = ImageFont.truetype("segoeui.ttf", 18)
    except OSError:
        font = small = ImageFont.load_default()
    pad = 30
    bw, bh = W * OUT, H * OUT
    page = Image.new("RGBA", (pad + len(variants) * (bw + pad), 80 + bh + 40 + H * 2 + 30), (24, 28, 22, 255))
    sd = ImageDraw.Draw(page)
    for i, (name, img) in enumerate(variants):
        x = pad + i * (bw + pad)
        sd.text((x, 28), f"{name} outline", fill=(237, 242, 233), font=font)
        page.alpha_composite(img.resize((bw, bh), Image.LANCZOS), (x, 80))
        sd.text((x, 80 + bh + 12), "in game, actual size:", fill=(171, 183, 166), font=small)
        page.alpha_composite(img.resize((W * 2, H * 2), Image.LANCZOS), (x, 80 + bh + 40))
        page.alpha_composite(img.resize((W, H), Image.LANCZOS), (x + W * 2 + 20, 80 + bh + 40))
    page.save(out / "run-over-outlines.png")
    print("Wrote", out / "run-over-outlines.png")


if __name__ == "__main__":
    main()
