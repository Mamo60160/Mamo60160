#!/usr/bin/env python3
"""Scrape the public contribution calendar (no token, no GraphQL).

GitHub serves the calendar as HTML at
https://github.com/users/<username>/contributions — the same fragment the
profile page uses. Parse the day cells and write data/contributions.json
with raw days plus derived stats.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Mamo60160"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"

HEADERS = {"User-Agent": f"profile-art/1.0 (github.com/{USERNAME})"}


def fetch() -> list[dict]:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # counts live in sibling <tool-tip for="<td id>"> elements:
    # "No contributions on August 31st." / "3 contributions on January 4th."
    counts_by_cell_id: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        text = tip.get_text(" ", strip=True)
        count = 0
        for token in text.replace(",", " ").split():
            if token.isdigit():
                count = int(token)
                break
        counts_by_cell_id[target] = count

    days = []
    for cell in soup.select("td[data-date], rect[data-date]"):
        d = cell.get("data-date")
        level = cell.get("data-level")
        if not d or level is None:
            continue
        count = counts_by_cell_id.get(cell.get("id"), 0)
        days.append({"date": d, "count": count, "level": int(level)})
    return days


def derive(days: list[dict]) -> dict:
    by_date = {d["date"]: d for d in days}
    dates = sorted(by_date)

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})

    def streaks(relevant: list[dict]) -> tuple[int, int]:
        longest = current = 0
        prev: date | None = None
        for d in relevant:
            if d["count"] == 0:
                current = 0
                prev = None
                continue
            cur = date.fromisoformat(d["date"])
            current = current + 1 if prev and cur - prev == timedelta(days=1) else 1
            longest = max(longest, current)
            prev = cur
        return longest, current

    ordered = [by_date[k] for k in dates]
    longest, current = streaks(ordered)

    monthly: dict[str, int] = defaultdict(int)
    for d in ordered:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "longest_streak": longest,
        "current_streak": current,
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    days = fetch()
    data = {"username": USERNAME, "updated": date.today().isoformat(),
            "days": days, "stats": derive(days)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    s = data["stats"]
    print(f"[fetch] {len(days)} days, {s['total']} contributions, "
          f"streak {s['current_streak']} (longest {s['longest_streak']})")
    print(f"[fetch] wrote {OUT}")


if __name__ == "__main__":
    main()
