#!/usr/bin/env python3
"""Generate info-card.svg: a neofetch-style panel that fades in line by line.

Edit the CONTENT dict below with your own details, then run:
    python scripts/make_info_card.py
Set STATIC=1 to emit a frozen frame (no animation) for local previews.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- EDIT ME ---
CONTENT = {
    "title": "mehmet@github:~ neofetch",
    "rows": [
        # (key, value, color)
        ("Now", "Data & IA Engineer @ Numspot", "#79c0ff"),
        ("School", "Epitech - 4th year, AI & Cloud major", "#d2a8ff"),
        ("Stack", "Python · ML · Cloud", "#7ee787"),
        ("Highlights", "Learning by shipping, every day", "#ffa657"),
    ],
    "footer": "github.com/Mamo60160",
}
# ----------------------------------------------------------------------------

WIDTH = 490
ROW_H = 34
PAD_X = 26
PAD_TOP = 56
BG = "#0d1117"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
GREEN = "#3fb950"

try:
    FONT = "'JetBrains Mono','Fira Code',Menlo,Consolas,monospace"
except Exception:  # pragma: no cover
    FONT = "monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    n = len(CONTENT["rows"])
    height = PAD_TOP + n * ROW_H + 46

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="neofetch info card">',
        f'<rect width="{WIDTH}" height="{height}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        # title bar with traffic lights
        '<circle cx="20" cy="20" r="6" fill="#ff5f57"/>',
        '<circle cx="38" cy="20" r="6" fill="#febc2e"/>',
        '<circle cx="56" cy="20" r="6" fill="#28c840"/>',
    ]

    title = CONTENT["title"]
    s.append(
        f'<text x="{WIDTH / 2}" y="25" text-anchor="middle" font-family="{FONT}" '
        f'font-size="13" fill="{DIM}">{esc(title)}</text>'
    )
    s.append(f'<line x1="0" y1="40" x2="{WIDTH}" y2="40" stroke="{BORDER}"/>')

    delay = 0.15
    for i, (key, value, color) in enumerate(CONTENT["rows"]):
        y = PAD_TOP + i * ROW_H
        anim = "" if static else _line_anim(delay, i)
        s.append(f'<g{anim}>')
        s.append(
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="14" '
            f'font-weight="bold" fill="{color}">{esc(key)}</text>'
        )
        s.append(
            f'<text x="{PAD_X + 130}" y="{y}" font-family="{FONT}" font-size="14" '
            f'fill="{FG}">{esc(value)}</text>'
        )
        s.append("</g>")
        delay += 0.25

    fy = PAD_TOP + n * ROW_H + 16
    anim = "" if static else _line_anim(delay, n + 1)
    s.append(f'<g{anim}>')
    s.append(f'<text x="{PAD_X}" y="{fy}" font-family="{FONT}" font-size="12" fill="{GREEN}">$ {esc(CONTENT["footer"])}</text>')
    s.append("</g>")

    s.append("</svg>")

    if not static:
        s.insert(1, _style())

    dest = ROOT / "info-card.svg"
    dest.write_text("\n".join(s), encoding="utf-8")
    print(f"[card] wrote {dest}{' (static)' if static else ''}")


def _style() -> str:
    return (
        "<style>"
        "@keyframes lineIn{from{opacity:0;transform:translateY(8px)}"
        "to{opacity:1;transform:translateY(0)}}"
        ".ln{opacity:0;animation:lineIn .4s ease-out forwards}"
        "</style>"
    )


def _line_anim(delay: float, idx: int) -> str:
    return f' class="ln" style="animation-delay:{delay:.2f}s"'


if __name__ == "__main__":
    main()
