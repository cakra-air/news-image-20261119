#!/usr/bin/env python3
"""Render a deterministic 1024x1024 news summary PNG for 19 Nov 2026.

Standard library only.  No clocks, no randomness, no network.  Running the
program twice yields byte-for-byte identical files.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Each glyph is seven rows of five cells; '#' paints, '.' skips.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "....#", "....#", "....#", "#...#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#...#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....",) * 7,
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}
BLANK = (".....",) * 7

HEADLINES = [
    "TRUMP XI PUTIN APEC SUMMIT IN SHENZHEN",
    "IRAN STRIKES US BASE IN KUWAIT",
    "CRIMEA BRIDGE HIT AGAIN",
    "VOYAGER 1 REACHES ONE LIGHT DAY",
    "UN REPORTS 4595 DEATHS IN HAITI",
    "MYANMAR GENOCIDE RULING DUE",
    "EU APPROVES INDONESIA TRADE DEAL",
]


class Canvas:
    """A tiny RGB framebuffer with rectangle and text drawing helpers."""

    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill(0, 0, width, height, color)

    def fill(self, x, y, w, h, color):
        row = bytes(color) * w
        stride = self.width * 3
        for yy in range(max(0, y), min(self.height, y + h)):
            start = yy * stride + max(0, x) * 3
            count = min(self.width, x + w) - max(0, x)
            if count > 0:
                self.pixels[start:start + count * 3] = row[:count * 3]

    def text(self, message, x, y, scale, color):
        cursor = x
        for char in message.upper():
            glyph = GLYPHS.get(char, BLANK)
            for ry, row in enumerate(glyph):
                for rx, cell in enumerate(row):
                    if cell == "#":
                        self.fill(cursor + rx * scale, y + ry * scale,
                                  scale, scale, color)
            cursor += 6 * scale
        return cursor

    def to_png(self):
        stride = self.width * 3
        scanlines = bytearray()
        for y in range(self.height):
            scanlines.append(0)  # PNG filter: None
            start = y * stride
            scanlines.extend(self.pixels[start:start + stride])
        return b"\x89PNG\r\n\x1a\n" + _chunk(
            b"IHDR", struct.pack(">IIBBBBB", self.width, self.height,
                                 8, 2, 0, 0, 0)) + _chunk(
            b"IDAT", zlib.compress(bytes(scanlines), 9)) + _chunk(b"IEND", b"")


def _chunk(tag, payload):
    return (struct.pack(">I", len(payload)) + tag + payload +
            struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))


def compose():
    night = (9, 14, 29)
    panel = (17, 28, 52)
    teal = (26, 178, 172)
    gold = (253, 196, 48)
    red = (232, 64, 84)
    paper = (245, 248, 252)
    dim = (34, 50, 82)
    mist = (158, 176, 204)

    image = Canvas(WIDTH, HEIGHT, night)

    # Masthead with a teal index tab.
    image.fill(0, 0, WIDTH, 138, panel)
    image.fill(0, 138, WIDTH, 6, gold)
    image.fill(56, 24, 10, 84, teal)
    image.text("WORLD NEWS", 82, 22, 9, paper)
    image.text("19 NOV 2026", 58, 100, 4, gold)

    # Headline column, framed by a continuous left accent rail.
    image.fill(44, 172, 4, 664, teal)
    top = 182
    step = 94
    for index, line in enumerate(HEADLINES):
        marker = gold if index % 2 == 0 else red
        image.fill(56, top + 1, 12, 26, marker)
        image.text(line, 86, top, 4, paper)
        image.fill(56, top + 40, WIDTH - 112, 2, dim)
        top += step

    # Footer strip.
    image.fill(0, HEIGHT - 84, WIDTH, 84, panel)
    image.fill(0, HEIGHT - 86, WIDTH, 2, red)
    image.text("THE DAILY DISPATCH - 19 NOV 2026 - MAKE.FUN EDITION",
               56, HEIGHT - 56, 3, mist)
    return image


def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    target = os.path.join(output_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(compose().to_png())


if __name__ == "__main__":
    main()
