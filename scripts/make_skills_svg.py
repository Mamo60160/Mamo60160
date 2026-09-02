#!/usr/bin/env python3
"""Generate skills-panel.svg: two-column panel.

Left  — `ls skills/` : animated level bars (SMIL width, staggered)
Right — `cat focus.txt` : now building / learning / goals, fading in

Edit the SKILLS and FOCUS lists below, then:
    python scripts/make_skills_svg.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- EDIT ME ---
SKILLS = [
    # (label, level %, bar color)
    ("Python", 90, "#7ee787"),
    ("AI / Machine Learning", 84, "#79c0ff"),
    ("Cloud & Infrastructure", 78, "#d2a8ff"),
    ("Data Engineering", 74, "#ffa657"),
]
FOCUS = [
    ("building", "Data & AI platform @ Numspot"),
    ("learning", "MLOps · cloud architecture"),
    ("goal", "ship open-source AI tooling"),
    ("open to", "AI & cloud collaborations"),
]
# ----------------------------------------------------------------------------

W = 860
H = 250
PAD = 30
BG = "#0d1117"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
GREEN = "#3fb950"
TRACK = "#21262d"

FONT = "'JetBrains Mono','Fira Code',Menlo,Consolas,monospace"
BAR_W = 350
BAR_H = 8


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="skills and focus">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        "<style>@keyframes lineIn{from{opacity:0;transform:translateY(6px)}"
        "to{opacity:1;transform:translateY(0)}}"
        ".ln{opacity:0;animation:lineIn .4s ease-out forwards}</style>",
    ]

    # ---- left column: skill bars -------------------------------------------
    s.append(
        f'<text class="ln" x="{PAD}" y="52" font-family="{FONT}" font-size="13" '
        f'fill="{GREEN}">$ ls skills/ --sort=level</text>'
    )
    y = 82
    delay = 0.35
    for i, (label, pct, color) in enumerate(SKILLS):
        anim = f' class="ln" style="animation-delay:{delay:.2f}s"'
        s.append(f'<g{anim}>')
        s.append(
            f'<text x="{PAD}" y="{y}" font-family="{FONT}" font-size="12.5" '
            f'fill="{FG}">{esc(label)}</text>'
        )
        s.append(
            f'<text x="{PAD + BAR_W}" y="{y}" text-anchor="end" font-family="{FONT}" '
            f'font-size="12" fill="{DIM}">{pct}%</text>'
        )
        s.append(
            f'<rect x="{PAD}" y="{y + 8}" width="{BAR_W}" height="{BAR_H}" rx="4" fill="{TRACK}"/>'
        )
        s.append(
            f'<rect x="{PAD}" y="{y + 8}" width="0" height="{BAR_H}" rx="4" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{BAR_W * pct // 100}" '
            f'begin="{delay + 0.15:.2f}s" dur="0.8s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/></rect>'
        )
        s.append("</g>")
        y += 40
        delay += 0.22

    # ---- right column: focus ------------------------------------------------
    rx = PAD + BAR_W + 90
    s.append(
        f'<text class="ln" style="animation-delay:.3s" x="{rx}" y="52" '
        f'font-family="{FONT}" font-size="13" fill="{GREEN}">$ cat focus.txt</text>'
    )
    fy = 82
    fdelay = 0.6
    for key, value in FOCUS:
        s.append(f'<g class="ln" style="animation-delay:{fdelay:.2f}s">')
        s.append(
            f'<text x="{rx}" y="{fy}" font-family="{FONT}" font-size="12.5" '
            f'fill="{GREEN}">▸ {esc(key)}</text>'
        )
        s.append(
            f'<text x="{rx + 92}" y="{fy}" font-family="{FONT}" font-size="12.5" '
            f'fill="{FG}">{esc(value)}</text>'
        )
        s.append("</g>")
        fy += 40
        fdelay += 0.22

    s.append("</svg>")
    dest = ROOT / "skills-panel.svg"
    dest.write_text("\n".join(s), encoding="utf-8")
    print(f"[skills] wrote {dest}")


if __name__ == "__main__":
    main()
