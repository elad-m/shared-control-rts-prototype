"""Builds the artillery-slayer mouse cursor, SCCArtillerySlayer.ani.

It is the game's own attack-move cursor (Data\\Cursors\\SCCAttMov.ani from the Zero Hour
install) recolored: the green arrows become black with a red edge, so the cursor is red and
black. Only palette indexes change; frames, timing and hotspot stay the same.

    python scripts/make-artillery-slayer-cursor.py [path\\to\\SCCAttMov.ani]

Writes resources/shared-control/Cursors/SCCArtillerySlayer.ani.
"""

import pathlib
import struct
import sys

DEFAULT_SOURCE = pathlib.Path(
    r"C:\Program Files\EA Games\Command and Conquer Generals Zero Hour"
    r"\Command and Conquer Generals Zero Hour\Data\Cursors\SCCAttMov.ani")
GREEN, RED, BLACK = (0, 255, 0), (255, 0, 0), (0, 0, 0)


def recolor_icon(icon):
    """Recolors one 4-bit .cur image in place (bytearray)."""
    offset = struct.unpack_from("<I", icon, 6 + 12)[0]
    header_size, width, height2, _, bpp = struct.unpack_from("<IiiHH", icon, offset)
    assert bpp == 4, bpp
    height = height2 // 2
    colors = struct.unpack_from("<I", icon, offset + 32)[0] or 16
    palette = offset + header_size
    rgb = [tuple(icon[palette + i * 4 + 2 - c] for c in range(3)) for i in range(colors)]
    green, red, black = rgb.index(GREEN), rgb.index(RED), rgb.index(BLACK)
    pixels = palette + colors * 4
    stride = ((width * 4 + 31) // 32) * 4

    def get(x, y):
        byte = icon[pixels + y * stride + x // 2]
        return (byte >> 4) if x % 2 == 0 else (byte & 15)

    def put(x, y, index):
        at = pixels + y * stride + x // 2
        icon[at] = (icon[at] & 0x0F) | (index << 4) if x % 2 == 0 else (icon[at] & 0xF0) | index

    old = [[get(x, y) for x in range(width)] for y in range(height)]
    for y in range(height):
        for x in range(width):
            if old[y][x] == green:
                put(x, y, black)
            elif old[y][x] == black and any(
                    0 <= x + dx < width and 0 <= y + dy < height and old[y + dy][x + dx] == green
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                put(x, y, red)


def recolor(data):
    data = bytearray(data)
    count = 0
    position = 12                          # past "RIFF", size, "ACON"
    while position + 8 <= len(data):
        tag = bytes(data[position:position + 4])
        size = struct.unpack_from("<I", data, position + 4)[0]
        if tag == b"LIST":
            position += 12                 # walk into the list
            continue
        if tag == b"icon":
            icon = data[position + 8:position + 8 + size]
            recolor_icon(icon)
            data[position + 8:position + 8 + size] = icon
            count += 1
        position += 8 + size + (size & 1)
    assert count, "no frames found"
    return bytes(data), count


def main():
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    data, count = recolor(source.read_bytes())
    root = pathlib.Path(__file__).resolve().parent.parent
    target = root / "resources" / "shared-control" / "Cursors" / "SCCArtillerySlayer.ani"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"Wrote {target} ({len(data)} bytes, {count} frames)")


if __name__ == "__main__":
    main()
