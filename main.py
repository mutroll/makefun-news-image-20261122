#!/usr/bin/env python3
"""news-image-20261122: a poster summing up Sunday 22 November 2026.

Draws a 1024x1024 newspaper poster with a pure-Python PNG writer
(standard library only: struct, zlib, os, math). No network, no fonts,
no image assets: every letter and picture is drawn by this program.

Stories (all happened or first reported on Sunday 22 Nov 2026):
  1. COP31 climate talks in Antalya near a final deal.
  2. Hong Kong's Election Committee polls open.
  3. A magnitude 4.1 earthquake shakes Myanmar.
  4. Israel's Yashar-Likud coalition talks open.
  5. The Las Vegas Grand Prix races today, Verstappen on pole.
  6. The Icons of Porsche festival opens in Dubai.

Writes the PNG to MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Deterministic: the same bytes on every run.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 227)   # warm newsprint cream
INK = (20, 38, 63)        # deep navy ink
RED = (192, 57, 43)       # masthead red
WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
TEAL = (14, 124, 123)
GREEN = (46, 139, 64)
BLUE = (41, 98, 168)
SKY = (135, 196, 235)
YELLOW = (240, 196, 25)
ORANGE = (230, 126, 34)
BROWN = (122, 79, 43)
GREY = (120, 124, 130)
LIGHTGREY = (226, 230, 232)

# ------------------------------------------------------------- 5x7 font ---
# Each glyph is 7 rows of 5 bits, '#' = ink. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
}


def text_width(s, scale):
    """Pixel width of s at the given scale (6 units per glyph, 5 + 1 gap)."""
    return len(s) * 6 * scale - scale


def wrap_words(s, max_chars):
    """Word-wrap s into lines of at most max_chars characters."""
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas --
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[0::3] = bytes([r]) * (self.w * self.h)
        self.px[1::3] = bytes([g]) * (self.w * self.h)
        self.px[2::3] = bytes([b]) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            n = x1 - x0
            self.px[base:base + n * 3:3] = bytes([color[0]]) * n
            self.px[base + 1:base + n * 3 + 1:3] = bytes([color[1]]) * n
            self.px[base + 2:base + n * 3 + 2:3] = bytes([color[2]]) * n

    def border(self, x, y, w, h, color, t=3):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color):
        for a, b in zip(points, points[1:]):
            self.line(a[0], a[1], b[0], b[1], color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=3):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, t, 1, color)
            self.rect(cx + dx - t + 1, cy + dy, t, 1, color)
        for dx in range(-r, r + 1):
            dy = int(math.sqrt(max(0, r * r - dx * dx)))
            self.rect(cx + dx, cy - dy, 1, t, color)
            self.rect(cx + dx, cy + dy - t + 1, 1, t, color)

    def triangle(self, p1, p2, p3, color):
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts
        if y1 == y3:
            return
        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(y1, y3 + 1):
            if y < y2:
                xa = interp(x1, y1, x2, y2, y)
                xb = interp(x1, y1, x3, y3, y)
            else:
                xa = interp(x2, y2, x3, y3, y)
                xb = interp(x1, y1, x3, y3, y)
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.rect(int(math.ceil(lo)), y, int(math.floor(hi)) - int(math.ceil(lo)) + 1, 1, color)

    def text(self, x, y, s, scale, color):
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch)
            if glyph is None:
                continue
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(ox + col * scale, y + row * scale, scale, scale, color)

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ------------------------------------------------------------------ scenes --
def scene_globe(c, cx, cy):
    """COP31: a globe under a bright sun."""
    c.circle(cx + 52, cy - 34, 13, YELLOW)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x1 = cx + 52 + int(19 * math.cos(a))
        y1 = cy - 34 + int(19 * math.sin(a))
        x2 = cx + 52 + int(26 * math.cos(a))
        y2 = cy - 34 + int(26 * math.sin(a))
        c.line(x1, y1, x2, y2, YELLOW)
    c.circle(cx - 6, cy + 4, 42, BLUE)
    c.ring(cx - 6, cy + 4, 42, INK, 3)
    c.circle(cx - 22, cy - 8, 12, GREEN)
    c.circle(cx + 8, cy + 12, 14, GREEN)
    c.circle(cx + 2, cy - 18, 9, GREEN)
    c.line(cx - 52, cy + 46, cx + 44, cy + 46, TEAL)
    c.line(cx - 40, cy + 52, cx + 32, cy + 52, TEAL)


def scene_ballot(c, cx, cy):
    """Hong Kong: a ballot box with a checked ballot."""
    c.rect(cx - 34, cy - 42, 26, 34, WHITE)
    c.border(cx - 34, cy - 42, 26, 34, INK, 3)
    for off in (0, 2, 4):
        c.line(cx - 30, cy - 26 + off, cx - 22, cy - 18 + off, RED)
        c.line(cx - 22, cy - 18 + off, cx - 12, cy - 36 + off, RED)
    c.rect(cx - 52, cy - 8, 104, 52, TEAL)
    c.border(cx - 52, cy - 8, 104, 52, INK, 3)
    c.rect(cx - 24, cy - 12, 48, 6, INK)
    c.text_center(cx, cy + 14, "VOTE", 3, WHITE)


def scene_quake(c, cx, cy):
    """Myanmar: shaking buildings, a crack and a seismograph trace."""
    c.rect(cx - 58, cy - 18, 34, 62, INK)
    c.rect(cx - 16, cy - 38, 34, 82, BROWN)
    c.rect(cx + 26, cy - 6, 30, 50, INK)
    for bx, by in ((-50, -8), (-38, -8), (-8, -28), (4, -28), (32, 4), (44, 4)):
        c.rect(cx + bx, cy + by, 7, 9, YELLOW)
    c.polyline([(cx - 70, cy + 48), (cx - 40, cy + 40), (cx - 22, cy + 50),
                (cx + 2, cy + 38), (cx + 26, cy + 48), (cx + 48, cy + 40),
                (cx + 70, cy + 48)], RED)
    c.polyline([(cx - 66, cy - 52), (cx - 50, cy - 58), (cx - 38, cy - 46),
                (cx - 24, cy - 60), (cx - 10, cy - 48), (cx + 4, cy - 58),
                (cx + 18, cy - 46), (cx + 32, cy - 56), (cx + 48, cy - 48),
                (cx + 62, cy - 54)], RED)


def scene_table(c, cx, cy):
    """Israel: a round table, two chairs, a document and an olive branch."""
    c.rect(cx - 78, cy - 6, 22, 44, INK)
    c.rect(cx + 56, cy - 6, 22, 44, INK)
    c.rect(cx - 78, cy - 12, 22, 8, INK)
    c.rect(cx + 56, cy - 12, 22, 8, INK)
    c.circle(cx, cy + 6, 46, BROWN)
    c.ring(cx, cy + 6, 46, INK, 3)
    c.rect(cx - 6, cy + 44, 12, 12, INK)
    c.rect(cx - 20, cy - 8, 40, 26, WHITE)
    c.border(cx - 20, cy - 8, 40, 26, INK, 2)
    c.line(cx - 14, cy + 0, cx + 14, cy + 0, INK)
    c.line(cx - 14, cy + 7, cx + 14, cy + 7, INK)
    c.line(cx - 14, cy + 14, cx + 2, cy + 14, INK)
    c.line(cx + 52, cy - 52, cx + 78, cy - 30, GREEN)
    for dx, dy in ((56, -50), (64, -44), (72, -38), (60, -46), (70, -40)):
        c.circle(cx + dx, cy + dy, 5, GREEN)
    c.circle(cx - 74, cy - 52, 5, GREEN)
    c.circle(cx - 66, cy - 46, 5, GREEN)


def scene_racecar(c, cx, cy):
    """Las Vegas GP: a formula car and a chequered flag."""
    c.rect(cx - 78, cy + 18, 130, 6, GREY)
    c.rect(cx - 70, cy - 6, 96, 16, RED)
    c.triangle((cx + 26, cy - 6), (cx + 26, cy + 10), (cx + 62, cy + 10), RED)
    c.rect(cx - 8, cy - 22, 30, 16, RED)
    c.circle(cx - 6, cy - 26, 9, INK)
    c.rect(cx - 78, cy - 18, 6, 22, INK)
    c.rect(cx - 84, cy - 24, 18, 6, INK)
    c.circle(cx - 52, cy + 12, 15, BLACK)
    c.circle(cx - 52, cy + 12, 6, LIGHTGREY)
    c.circle(cx + 34, cy + 12, 15, BLACK)
    c.circle(cx + 34, cy + 12, 6, LIGHTGREY)
    c.line(cx - 88, cy - 2, cx - 66, cy - 2, YELLOW)
    c.line(cx - 92, cy + 6, cx - 72, cy + 6, YELLOW)
    c.line(cx + 76, cy - 52, cx + 76, cy - 6, INK)
    for r in range(3):
        for col in range(4):
            colr = BLACK if (r + col) % 2 == 0 else WHITE
            c.rect(cx + 78 + col * 7, cy - 52 + r * 7, 7, 7, colr)
    c.border(cx + 78, cy - 52, 28, 21, INK, 2)


def scene_sportscar(c, cx, cy):
    """Dubai: a sleek sports car under a palm and the sun."""
    c.circle(cx - 72, cy - 38, 12, YELLOW)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x1 = cx - 72 + int(18 * math.cos(a))
        y1 = cy - 38 + int(18 * math.sin(a))
        x2 = cx - 72 + int(25 * math.cos(a))
        y2 = cy - 38 + int(25 * math.sin(a))
        c.line(x1, y1, x2, y2, YELLOW)
    c.line(cx + 76, cy - 6, cx + 72, cy + 30, BROWN)
    c.line(cx + 76, cy - 6, cx + 76, cy + 30, BROWN)
    c.line(cx + 76, cy - 6, cx + 80, cy + 30, BROWN)
    for (ex, ey) in ((60, -16), (66, -20), (86, -20), (92, -16), (76, -24)):
        c.line(cx + 76, cy - 6, cx + ex, cy + ey, GREEN)
    c.rect(cx - 84, cy + 30, 140, 5, GREY)
    c.rect(cx - 76, cy + 6, 124, 16, ORANGE)
    c.triangle((cx - 76, cy + 6), (cx - 76, cy + 22), (cx - 48, cy + 22), ORANGE)
    c.triangle((cx + 48, cy + 6), (cx + 48, cy + 22), (cx + 62, cy + 22), ORANGE)
    c.rect(cx - 44, cy - 8, 52, 14, ORANGE)
    c.rect(cx - 38, cy - 4, 40, 10, SKY)
    c.circle(cx - 52, cy + 22, 13, BLACK)
    c.circle(cx - 52, cy + 22, 5, LIGHTGREY)
    c.circle(cx + 30, cy + 22, 13, BLACK)
    c.circle(cx + 30, cy + 22, 5, LIGHTGREY)


# ------------------------------------------------------------------ poster --
PANELS = [
    ("CLIMATE - ANTALYA, TURKIYE", "COP31 NEARS A FINAL DEAL",
     "NEW PACKAGE UNVEILED AS TALKS RUN INTO OVERTIME", scene_globe),
    ("POLITICS - HONG KONG", "HONG KONG VOTES TODAY",
     "856 CANDIDATES FOR 723 SEATS ON ELECTION COMMITTEE", scene_ballot),
    ("DISASTER - MYANMAR", "M4.1 QUAKE SHAKES MYANMAR",
     "TREMOR FELT IN THE EARLY HOURS OF SUNDAY", scene_quake),
    ("POLITICS - ISRAEL", "ISRAEL TALKS OPEN TODAY",
     "YASHAR AND LIKUD MEET TO BREAK DEADLOCK", scene_table),
    ("SPORT - LAS VEGAS", "LAS VEGAS GP RACES TODAY",
     "VERSTAPPEN ON POLE AS THE STRIP LIGHTS UP", scene_racecar),
    ("CULTURE - DUBAI", "PORSCHE FESTIVAL OPENS",
     "SHEIKH MANSOOR TOURS OPENING DAY IN DUBAI", scene_sportscar),
]


def draw_panel(c, x, y, w, h, kicker, headline, sub, scene):
    c.rect(x, y, w, h, WHITE)
    c.border(x, y, w, h, INK, 3)
    c.rect(x, y, w, 32, INK)
    c.text(x + 14, y + 9, kicker, 2, WHITE)
    scene(c, x + w // 2, y + 96)
    head_lines = wrap_words(headline, 25)
    hy = y + 158
    for line in head_lines[:2]:
        c.text(x + 14, hy, line, 3, INK)
        hy += 24
    sub_lines = wrap_words(sub, 38)
    sy = y + 206
    for line in sub_lines[:2]:
        c.text(x + 14, sy, line, 2, (60, 66, 74))
        sy += 17


def draw_poster():
    c = Canvas(W, H, PAPER)
    # masthead
    c.rect(0, 0, W, 152, INK)
    c.text_center(W // 2, 12, "SUNDAY", 10, WHITE)
    c.text_center(W // 2, 90, "22 NOVEMBER 2026", 7, YELLOW)
    c.rect(0, 152, W, 6, RED)
    # six panels, 2 columns x 3 rows
    pw, ph, gap = 488, 246, 16
    for i, (kicker, headline, sub, scene) in enumerate(PANELS):
        px = 16 + (i % 2) * (pw + gap)
        py = 170 + (i // 2) * (ph + 14)
        draw_panel(c, px, py, pw, ph, kicker, headline, sub, scene)
    # footer
    c.rect(16, 944, W - 32, 3, RED)
    c.text_center(W // 2, 958,
                  "ALSO TODAY: HONG KONG POLLS CLOSE AT 6PM - COP31 DEAL STILL TO BE SEALED",
                  2, INK)
    c.text_center(W // 2, 984,
                  "F1 RACE UNDER THE LAS VEGAS LIGHTS - SOURCES: ANI, REUTERS, AP",
                  2, INK)
    return c


def png_bytes(c):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw.extend(c.px[y * c.w * 3:(y + 1) * c.w * 3])

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_poster())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
