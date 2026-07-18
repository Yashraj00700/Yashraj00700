#!/usr/bin/env python3
"""Scrape the public GitHub contributions calendar (no auth token needed)."""
import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "Yashraj00700")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(username: str) -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        raise RuntimeError("No contribution cells found — GitHub markup may have changed")

    days = []
    for cell in cells:
        days.append(
            {
                "date": cell["data-date"],
                "level": int(cell.get("data-level", 0)),
            }
        )
    days.sort(key=lambda d: d["date"])
    return days


def main() -> None:
    days = fetch_days(USERNAME)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"username": USERNAME, "days": days}, indent=2))
    print(f"Wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
