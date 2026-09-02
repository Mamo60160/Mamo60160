#!/usr/bin/env python3
"""Generate boot-banner.svg: a fake SSH session that types itself in.

Command lines are typed with a clip-wipe + riding cursor (SMIL), output
lines fade in (CSS keyframes). Live data comes from data/contributions.json
and data/activity.json so the daily cron keeps it fresh. Plays once, then a
blinking cursor loops.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

W = 860
PAD = 24
FONT = "'JetBrains Mono','Fira Code',Menlo,Consolas,monospace"
BG = "#0d1117"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
GREEN = "#7ee787"
BLUE = "#79c0ff"
YELLOW = "#ffa657"

FS = 13
CHAR_W = 7.8
LINE_H = 27
TYPE_DUR = 0.5

GREEN_PROMPT = "#3fb950"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rel_time(iso: str) -> str:
    try:
        raw = iso.replace(" UTC", "+00:00").replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        s = (datetime.now(timezone.utc) - dt).total_seconds()
        if s < 90:
            return "just now"
        if s < 3600:
            return f"{int(s // 60)}m ago"
        if s < 86400:
            return f"{int(s // 3600)}h ago"
        return f"{int(s // 86400)}d ago"
    except Exception:
        return ""


def load() -> tuple[dict, list[dict]]:
    stats = {}
    try:
        stats = json.loads((ROOT / "data" / "contributions.json")
                           .read_text(encoding="utf-8"))["stats"]
    except Exception:
        pass
    events = []
    try:
        events = json.loads((ROOT / "data" / "activity.json")
                            .read_text(encoding="utf-8"))["events"]
    except Exception:
        pass
    return stats, events


def main() -> None:
    stats, events = load()
    st = stats or {"total": 0, "current_streak": 0, "longest_streak": 0,
                   "best_day": {"count": 0}}
    push = events[0] if events else None

    lines: list[tuple[str, str, str]] = []  # (kind, text, color)
    lines.append(("cmd", "ssh mehmet@numspot.io", ""))
    lines.append(("out", "connected ✓ — Data & IA Engineer (alternance) @ Numspot", BLUE))
    lines.append(("out", "Epitech · 4th year · AI & Cloud major", BLUE))
    lines.append(("cmd", "./status.sh --live", ""))
    lines.append(("out", "{:,} contributions · streak {} · best {}/day".format(
        st["total"], st["current_streak"], st["best_day"]["count"]), GREEN))
    if push_line := _push_line(events):
        lines.append(("out", push_line, DIM))

    h = 46 + len(lines) * (LINE_H := 27) + 46
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="terminal intro">',
        f'<rect width="{W}" height="{h}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        '<circle cx="20" cy="20" r="6" fill="#ff5f57"/>',
        '<circle cx="38" cy="20" r="6" fill="#febc2e"/>',
        '<circle cx="56" cy="20" r="6" fill="#28c840"/>',
        f'<text x="{W / 2}" y="25" text-anchor="middle" font-family="{FONT}" '
        f'font-size="13" fill="{DIM}">mehmet@github: ~/profile</text>',
        f'<line x1="0" y1="40" x2="{W}" y2="40" stroke="{BORDER}"/>',
        "<style>@keyframes lineIn{from{opacity:0;transform:translateY(6px)}"
        "to{opacity:1;transform:translateY(0)}}"
        ".out{opacity:0;animation:lineIn .35s ease-out forwards}</style>",
    ]

    y = 68
    begin = 0.3
    for i, (kind, text, color) in enumerate(lines):
        if kind == "cmd":
            s += _typed(i, y, text, begin)
        else:
            s.append(
                f'<text class="out" style="animation-delay:{begin:.2f}s" '
                f'x="46" y="{y}" font-family="{FONT}" font-size="{FS}" '
                f'fill="{color}" xml:space="preserve">{esc(text)}</text>'
            )
        y += LINE_H
        begin += 0.45

    # final prompt with an eternally blinking block cursor
    s.append(f'<text x="24" y="{y}" font-family="{FONT}" font-size="{FS}" fill="{GREEN_PROMPT}">$</text>')
    s.append(
        f'<rect x="46" y="{y - FS + 3}" width="9" height="{FS + 2}" fill="{FG}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
        f'dur="1.1s" repeatCount="indefinite"/></rect>'
    )

    s.append("</svg>")
    (ROOT / "boot-banner.svg").write_text("\n".join(s), encoding="utf-8")
    print("[boot] wrote boot-banner.svg")


def _push_line(events: list[dict]) -> str:
    if not events:
        return "last push: (building in private)"
    e = events[0]
    title = e["title"] or "push"
    # atom feed titles look like "Mamo60160 pushed municipall-backend-public"
    title = re.sub(r"^\S+ (pushed|created repository|created branch|deleted) ?", "", title)
    what = title or e["repo"] or "github"
    when = rel_time(e["updated"])
    return f"last push → {what[:60]} · {when}".rstrip(" ·")


def _typed(idx: int, y: int, text: str, begin: float) -> list[str]:
    x = 46
    w = len(text) * CHAR_W + 8
    clip_id = f"type{idx}"
    cur_id = f"tcur{idx}"
    return [
        f'<text x="24" y="{y}" font-family="{FONT}" font-size="{FS}" fill="{GREEN_PROMPT}">$</text>',
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y - FS}" width="0" height="{FS + 6}">'
        f'<animate attributeName="width" from="0" to="{w}" begin="{begin:.2f}s" '
        f'dur="0.4s" fill="freeze"/></rect></clipPath>',
        f'<g clip-path="url(#{clip_id})">'
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{FS}" fill="{FG}" '
        f'xml:space="preserve">{esc(text)}</text></g>',
        f'<rect id="{cur_id}" x="{x}" y="{y - FS + 2}" width="8" height="{FS + 1}" '
        f'fill="{FG}" opacity="0.9">'
        f'<animate attributeName="x" from="{x}" to="{x + w - 8}" begin="{begin:.2f}s" '
        f'dur="0.4s" fill="freeze"/>'
        f'<animate attributeName="opacity" from="0.9" to="0" '
        f'begin="{begin + 0.4:.2f}s" dur="0.06s" fill="freeze"/></rect>',
    ]


if __name__ == "__main__":
    main()
