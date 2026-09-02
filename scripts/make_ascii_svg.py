#!/usr/bin/env python3
"""Convert assets/source-prepped.png into a self-typing ASCII SVG (avi-ascii.svg).

Design choices:
- monochrome: one light-gray fill, no per-character colors
- high contrast: bright areas collapse to the space glyph
- animation: each row wipes left-to-right inside a clip, staggered top to
  bottom, plays once and freezes (SMIL, works inside GitHub <img>)
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9.1
    RESAMPLE = Image.LANCZOS

COLS = 100
ROWS = 53
FONT_SIZE = 12.5
CHAR_W = 7.5
LINE_H = 13.0
PAD = 16
FILL = "#c9d1d9"
BG = "#0d1117"
CURSOR_W = 9.0
ROW_STAGGER = 0.028  # seconds between rows
WIPE_DUR = 0.16      # seconds per-row wipe


def build_grid() -> list[str]:
    img = Image.open(ROOT / "assets" / "source-prepped.png").convert("L")
    img = img.resize((COLS, ROWS), RESAMPLE)
    px = img.load()
    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            level = 255 - px[x, y]  # 0 bright -> 255 dark
            idx = round(level / 255 * (len(RAMP) - 1))
            row.append(RAMP[idx])
        grid.append("".join(row).rstrip() or " ")
    return grid


def main() -> None:
    grid = build_grid()
    w = PAD * 2 + COLS * CHAR_W
    h = PAD * 2 + ROWS * LINE_H

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="ASCII portrait">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
    ]

    for y, text in enumerate(grid):
        if not text.strip():
            continue
        top = PAD + y * LINE_H
        clip_id = f"row{y}"
        out.append(f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{top - 2}" width="0" height="{LINE_H}">')
        out.append(
            f'<animate attributeName="width" from="0" to="{COLS * CHAR_W + PAD}" '
            f'begin="{y * ROW_STAGGER:.3f}s" dur="{WIPE_DUR}s" fill="freeze"/>'
        )
        out.append("</rect></clipPath>")
        out.append(f'<g clip-path="url(#{clip_id})">')
        out.append(
            f'<text x="{PAD}" y="{top + FONT_SIZE}" font-family="Menlo, Consolas, monospace" '
            f'font-size="{FONT_SIZE}" fill="{FILL}" xml:space="preserve">{esc(text)}</text>'
        )
        # small block "cursor" riding the wipe edge
        cursor_id = f"cur{y}"
        out.append(f'<rect id="{cursor_id}" x="{PAD}" y="{top - 2}" width="{CURSOR_W}" height="{LINE_H}" fill="{FILL}" opacity="0.9">')
        out.append(
            f'<animate attributeName="x" from="{PAD}" to="{PAD + COLS * CHAR_W}" '
            f'begin="{y * ROW_STAGGER:.3f}s" dur="{WIPE_DUR}s" fill="freeze"/>'
        )
        out.append(f'<animate attributeName="opacity" from="0.9" to="0" begin="{y * ROW_STAGGER + WIPE_DUR:.3f}s" dur="0.05s" fill="freeze"/>')
        out.append("</rect>")
        out.append("</g>")

    out.append("</svg>")
    dest = ROOT / "avi-ascii.svg"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"[ascii] wrote {dest} ({COLS}x{ROWS} grid)")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
