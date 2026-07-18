#!/usr/bin/env python3
"""Render the contributions calendar as a self-contained animated SVG.

Boxes reveal diagonally (week + day order) using CSS keyframes, then freeze.
No JS, no external fonts/images — just <rect> + <style>, which GitHub renders
and animates when embedded via <img> in a README.
"""
import json
from datetime import date
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GAP = 3
MARGIN_LEFT = 24
MARGIN_TOP = 10
STAGGER = 0.012  # seconds between diagonally-adjacent cells

# Matches avi-ascii.svg width (414.4) + info-card.svg width (490) so the
# heatmap's edges line up flush with the two-column row beneath it.
TARGET_WIDTH = 904.4


def load_weeks() -> list[list[dict]]:
    payload = json.loads(DATA_PATH.read_text())
    days = payload["days"]

    # Bucket into weeks starting on Sunday, matching GitHub's own calendar layout.
    weeks: list[list[dict]] = []
    current_week: list[dict] = []
    for day in days:
        y, m, d = (int(p) for p in day["date"].split("-"))
        weekday = date(y, m, d).isoweekday() % 7  # Sunday -> 0
        if weekday == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        while len(current_week) < weekday:
            current_week.append(None)
        current_week.append(day)
    if current_week:
        weeks.append(current_week)
    return weeks


def render(weeks: list[list[dict]]) -> str:
    n_weeks = len(weeks)
    step = (TARGET_WIDTH - MARGIN_LEFT - GAP) / n_weeks
    cell = step - GAP
    width = MARGIN_LEFT + n_weeks * step + GAP
    height = MARGIN_TOP + 7 * step + GAP

    rects = []
    max_delay = 0.0
    for wi, week in enumerate(weeks):
        for di in range(7):
            day = week[di] if di < len(week) else None
            level = day["level"] if day else 0
            color = LEVEL_COLORS[min(level, 4)]
            x = MARGIN_LEFT + wi * step
            y = MARGIN_TOP + di * step
            delay = (wi + di) * STAGGER
            max_delay = max(max_delay, delay)
            title = f"{day['date']}: level {level}" if day else ""
            rects.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="2.5" ry="2.5" '
                f'fill="{color}" class="cell" style="animation-delay:{delay:.3f}s">'
                f'{f"<title>{title}</title>" if title else ""}</rect>'
            )

    duration = 0.35
    total_time = max_delay + duration

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" width="{width:.2f}" height="{height:.2f}">
  <style>
    .bg {{ fill: transparent; }}
    .cell {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      transform: scale(0.3) translateY(-6px);
      animation-name: reveal;
      animation-duration: {duration}s;
      animation-timing-function: ease-out;
      animation-fill-mode: forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: scale(0.3) translateY(-6px); }}
      60%  {{ opacity: 1; transform: scale(1.08) translateY(0); }}
      100% {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}
  </style>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" />
  {''.join(rects)}
</svg>
"""
    return svg


def main() -> None:
    weeks = load_weeks()
    svg = render(weeks)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
