#!/usr/bin/env python3
"""Draw one deterministic 1024x1024 PNG summing up the world news of 19 Nov 2026.

Runs offline in the grader sandbox and writes /output/entry.png.
No network and no randomness: two runs produce byte-identical output.
"""
import os
import struct
import zlib

W = H = 1024

FONT = {
    'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'B': ('####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'),
    'C': ('.####', '#....', '#....', '#....', '#....', '#....', '.####'),
    'D': ('####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'),
    'E': ('#####', '#....', '#....', '####.', '#....', '#....', '#####'),
    'F': ('#####', '#....', '#....', '####.', '#....', '#....', '#....'),
    'G': ('.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'),
    'H': ('#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'I': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '#####'),
    'J': ('..###', '....#', '....#', '....#', '#...#', '#...#', '.###.'),
    'K': ('#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'),
    'L': ('#....', '#....', '#....', '#....', '#....', '#....', '#####'),
    'M': ('#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#', '#...#'),
    'N': ('#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'P': ('####.', '#...#', '#...#', '####.', '#....', '#....', '#....'),
    'Q': ('.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'),
    'R': ('####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'),
    'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
    'T': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'),
    'U': ('#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'V': ('#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'),
    'W': ('#...#', '#...#', '#...#', '#...#', '#.#.#', '##.##', '#...#'),
    'X': ('#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'),
    'Y': ('#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'),
    'Z': ('#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'),
    '0': ('.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'),
    '1': ('..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'),
    '2': ('.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'),
    '3': ('####.', '....#', '....#', '.###.', '....#', '....#', '####.'),
    '4': ('...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'),
    '5': ('#####', '#....', '####.', '....#', '....#', '#...#', '.###.'),
    '6': ('.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'),
    '7': ('#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'),
    '8': ('.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'),
    '9': ('.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'),
    ' ': ('.....', '.....', '.....', '.....', '.....', '.....', '.....'),
    '-': ('.....', '.....', '.....', '#####', '.....', '.....', '.....'),
    '.': ('.....', '.....', '.....', '.....', '.....', '.##..', '.##..'),
    ':': ('.....', '.##..', '.##..', '.....', '.##..', '.##..', '.....'),
    '/': ('....#', '....#', '...#.', '..#..', '.#...', '#....', '#....'),
}


def blank():
    return bytearray(W * H * 3)


def setpx(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def rect(px, x0, y0, w, h, color):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            setpx(px, x, y, color)


def draw_text(px, s, x, y, scale, color):
    cx = x
    for ch in s.upper():
        rows = FONT.get(ch, FONT[' '])
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '#':
                    rect(px, cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data +
            struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))


def write_png(path, px):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main():
    px = blank()
    BG = (12, 16, 34)
    TEAL = (16, 122, 138)
    GOLD = (250, 196, 64)
    RED = (220, 62, 76)
    WHITE = (244, 247, 252)
    DIM = (48, 66, 96)
    GREY = (158, 172, 196)

    rect(px, 0, 0, W, H, BG)
    rect(px, 0, 0, W, 124, TEAL)
    rect(px, 0, 124, W, 6, GOLD)
    draw_text(px, 'WORLD NEWS', 60, 20, 9, WHITE)
    draw_text(px, '19 NOV 2026', 60, 92, 4, GOLD)

    headlines = [
        'TRUMP XI PUTIN SUMMIT IN SHENZHEN',
        'IRAN STRIKES US BASE IN KUWAIT',
        'CRIMEA BRIDGE HIT THIRD TIME',
        'VOYAGER 1 REACHES ONE LIGHT DAY',
        'UN: 4595 DEAD IN HAITI VIOLENCE',
        'MYANMAR GENOCIDE RULING DUE',
        'EU APPROVES INDONESIA TRADE DEAL',
    ]
    accents = [GOLD, RED, GOLD, RED, GOLD, RED, GOLD]
    y = 170
    for i, line in enumerate(headlines):
        rect(px, 60, y + 2, 14, 14, accents[i % len(accents)])
        draw_text(px, line, 92, y, 4, WHITE)
        rect(px, 60, y + 36, W - 120, 2, DIM)
        y += 94

    rect(px, 60, H - 76, W - 120, 2, GOLD)
    rect(px, 0, H - 72, W, 72, (20, 32, 54))
    draw_text(px, 'ONE IMAGE OF THE DAY - 19 NOV 2026', 60, H - 52, 3, GREY)

    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    write_png(os.path.join(outdir, 'entry.png'), px)


if __name__ == '__main__':
    main()
