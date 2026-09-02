#!/usr/bin/env python3
"""Scrape the public activity feed (https://github.com/<user>.atom, no token)
and write data/activity.json with the latest public pushes.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Mamo60160"
URL = f"https://github.com/{USERNAME}.atom"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "activity.json"
HEADERS = {"User-Agent": f"profile-art/1.0 (github.com/{USERNAME})"}


def main() -> None:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    for entry in soup.find_all("entry"):
        title = entry.title.get_text(" ", strip=True) if entry.title else ""
        link = entry.link.get("href", "") if entry.link else ""
        updated = entry.updated.get_text(strip=True) if entry.updated else ""
        m = re.search(r"github\.com/[^/]+/([^/]+)/", link)
        repo = m.group(1) if m else ""
        events.append({"title": title, "repo": repo, "updated": updated})

    data = {"username": USERNAME, "updated": date.today().isoformat(),
            "events": events[:5]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[activity] {len(data['events'])} events -> {OUT}")


if __name__ == "__main__":
    main()
