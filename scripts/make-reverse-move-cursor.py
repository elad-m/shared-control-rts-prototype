"""Builds the reverse-move mouse cursor, SCCReverseMove.ani.

The cursor is original artwork in the style of the game's move cursor: two of its green
arrowheads in a line, pointing down at the spot that will be clicked, with a yellow
highlight stepping from the upper arrow to the lower one to show the direction of travel.

    python scripts/make-reverse-move-cursor.py [--preview preview.png]

Needs Pillow. Writes resources/shared-control/Cursors/SCCReverseMove.ani.
"""

import argparse
import pathlib
import struct

from PIL import Image, ImageDraw

SIZE = 32
HOTSPOT = (15, 27)          # the yellow dot: where the click lands
GREEN = (0, 255, 0, 255)    # the move cursor's own colors
YELLOW = (255, 255, 0, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
JIFFIES_PER_FRAME = 9       # 1/60 s units; three frames make a half-second loop

# Each arrowhead is a triangle pointing down: (left, top), (right, top), (tip).
UPPER_ARROW = [(8, 1), (22, 1), (15, 10)]
LOWER_ARROW = [(8, 12), (22, 12), (15, 21)]


def draw_frame(upper_color, lower_color):
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for points, color in ((UPPER_ARROW, upper_color), (LOWER_ARROW, lower_color)):
        draw.polygon(points, fill=color, outline=BLACK)
    x, y = HOTSPOT
    draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=YELLOW, outline=BLACK)
    draw.point((x, y), fill=WHITE)
    return image


def to_cur(image):
    """One 32-bit .cur image: ICONDIR, one entry, BITMAPINFOHEADER, pixels, AND mask."""
    width, height = image.size
    pixels = image.load()
    color_rows, mask_rows = bytearray(), bytearray()
    for y in range(height - 1, -1, -1):        # bitmap rows run bottom-up
        mask_bits = 0
        for x in range(width):
            r, g, b, a = pixels[x, y]
            color_rows += bytes((b, g, r, a))
            mask_bits = (mask_bits << 1) | (1 if a == 0 else 0)
        mask_rows += mask_bits.to_bytes(width // 8, "big")
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, len(color_rows) + len(mask_rows), 0, 0, 0, 0)
    body = header + bytes(color_rows) + bytes(mask_rows)
    directory = struct.pack("<HHH", 0, 2, 1)
    entry = struct.pack("<BBBBHHII", width, height, 0, 0, HOTSPOT[0], HOTSPOT[1], len(body), 6 + 16)
    return directory + entry + body


def chunk(tag, payload):
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def to_ani(frames):
    header = struct.pack("<9I", 36, len(frames), len(frames), 0, 0, 0, 0, JIFFIES_PER_FRAME, 1)
    frame_list = b"fram" + b"".join(chunk(b"icon", to_cur(frame)) for frame in frames)
    body = b"ACON" + chunk(b"anih", header) + chunk(b"LIST", frame_list)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", help="also write an enlarged PNG of the frames")
    args = parser.parse_args()

    frames = [draw_frame(YELLOW, GREEN), draw_frame(GREEN, YELLOW), draw_frame(GREEN, GREEN)]

    root = pathlib.Path(__file__).resolve().parent.parent
    target = root / "resources" / "shared-control" / "Cursors" / "SCCReverseMove.ani"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(to_ani(frames))
    print(f"Wrote {target} ({target.stat().st_size} bytes, {len(frames)} frames)")

    if args.preview:
        scale = 8
        sheet = Image.new("RGBA", (len(frames) * (SIZE + 2) * scale, SIZE * scale), (58, 70, 48, 255))
        for index, frame in enumerate(frames):
            big = frame.resize((SIZE * scale, SIZE * scale), Image.NEAREST)
            sheet.alpha_composite(big, (index * (SIZE + 2) * scale, 0))
        sheet.save(args.preview)
        print(f"Wrote preview {args.preview}")


if __name__ == "__main__":
    main()
