#!/usr/bin/env python3
"""Render data/contributions.json as contrib-heatmap.svg.

53-week x 7-day calendar of rounded boxes in a GitHub-ish green ramp,
revealed once with a diagonal slide-down (CSS keyframes, plays on load
then freezes), plus a Less->More legend and a stats footer.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 2
STEP = CELL + GAP
WEEKS = 53
MARGIN_L = 30          # room for weekday labels
MARGIN_T = 24          # room for month labels
USERNAME = "Mamo60160"

FONT = "'JetBrains Mono','Fira Code',Menlo,Consolas,monospace"
FG = "#e6edf3"
DIM = "#8b949e"
BG = "#0d1117"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    """Bucket days into 53 columns aligned on weeks starting Sunday."""
    by_date = {d["date"]: d for d in days}
    first = date.fromisoformat(days[0]["date"])
    # shift back to the Sunday that starts the first week
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks: list[list[dict | None]] = []
    for w in range(WEEKS):
        col: list[dict | None] = []
        for d in range(7):
            day = start + timedelta(days=w * 7 + d)
            col.append(by_date.get(day.isoformat()))
        weeks.append(col)
    return weeks


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    data = json.loads(DATA.read_text(encoding="utf-8"))
    stats = data["stats"]
    weeks = build_weeks(data["days"])

    grid_w = MARGIN_L + WEEKS * STEP
    grid_h = MARGIN_T + 7 * STEP
    footer_y = grid_h + 34
    w = grid_w + 12
    h = footer_y + 16

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{stats["total"]} contributions in the last year">',
        f'<rect width="{w}" height="{h}" rx="10" fill="{BG}" stroke="#30363d"/>',
    ]
    if not static:
        s.append(_style())

    # month labels along the top
    prev_month = None
    for wi, col in enumerate(weeks):
        first_day = next((d for d in col if d), None)
        if first_day is None:
            continue
        m = int(first_day["date"][5:7]) - 1
        if m != prev_month and wi < WEEKS - 1:
            s.append(
                f'<text x="{MARGIN_L + wi * STEP}" y="15" font-family="{FONT}" '
                f'font-size="10" fill="{DIM}">{MONTHS[m]}</text>'
            )
            prev_month = m

    # weekday labels (Mon / Wed / Fri)
    for dy, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s.append(
            f'<text x="18" y="{MARGIN_T + dy * STEP + CELL - 2}" text-anchor="end" '
            f'font-family="{FONT}" font-size="10" fill="{DIM}">{label}</text>'
        )

    # the grid: one group per week, revealed with a staggered diagonal slide
    delay = 0.0
    for wi, col in enumerate(weeks):
        x = MARGIN_L + wi * STEP
        anim = "" if static else _col_anim(delay)
        s.append(f'<g{anim}>')
        for di, day in enumerate(col):
            if day is None:
                continue
            y = MARGIN_T + di * STEP
            color = PALETTE[min(day["level"], len(PALETTE) - 1)]
            s.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
            )
        s.append("</g>")
        delay += 0.012  # diagonal sweep, ~0.64s total

    # legend
    ly = grid_h + 4
    s.append(
        f'<text x="{grid_w - 6 * STEP - 14}" y="{ly + CELL}" font-family="{FONT}" '
        f'font-size="10" fill="{DIM}">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        lx = grid_w - 6 * STEP + i * STEP
        s.append(
            f'<rect x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
        )
    s.append(
        f'<text x="{grid_w - 6 * STEP + 6 * STEP + 3}" y="{ly + CELL}" '
        f'font-family="{FONT}" font-size="10" fill="{DIM}">More</text>'
    )

    # stats footer
    st = stats
    total_txt = "{:,} contributions in the last year".format(st["total"])
    s.append(
        f'<text x="18" y="{footer_y + 6}" font-family="{FONT}" font-size="12" fill="{FG}">'
        f'{esc(total_txt)}'
        f'</text>'
    )
    s.append(
        f'<text x="{w - 18}" y="{footer_y + 6}" text-anchor="end" font-family="{FONT}" '
        f'font-size="11" fill="{DIM}">'
        f'streak {st["current_streak"]} · best {st["best_day"]["count"]} · @{esc(USERNAME)}'
        f'</text>'
    )

    s.append("</svg>")
    OUT.write_text("\n".join(s), encoding="utf-8")
    print(f"[heatmap] wrote {OUT} ({stats['total']} contributions)")


def _style() -> str:
    return (
        "<style>"
        "@keyframes colIn{from{opacity:0;transform:translateY(-14px)}"
        "to{opacity:1;transform:translateY(0)}}"
        ".wk{opacity:0;animation:colIn .45s ease-out forwards}"
        "</style>"
    )


def _col_anim(delay: float) -> str:
    return f' class="wk" style="animation-delay:{delay:.3f}s"'


if __name__ == "__main__":
    main()
