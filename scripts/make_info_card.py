#!/usr/bin/env python3
"""Render a neofetch-style info card as a self-contained animated SVG.

Lines fade + slide in with staggered delays, then freeze — no external
fonts, no JS, just <text> + CSS keyframes.
"""
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"

USERNAME = "Yashraj00700"
LINE_HEIGHT = 26
PAD_X = 22
PAD_TOP = 34
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
ACCENT = "#39d353"
DIM = "#8b949e"
FG = "#c9d1d9"

LINES = [
    ("prompt", f"{USERNAME}@github", None),
    ("rule", "-" * (len(f"{USERNAME}@github")), None),
    ("kv", "role", "AI Developer / Automation Builder"),
    ("kv", "focus", "AI SaaS, Computer Vision, Full-Stack"),
    ("kv", "languages", "Python, TypeScript, JavaScript"),
    ("kv", "stack", "React, Next.js, Node.js, Express, Tailwind"),
    ("kv", "philosophy", "build fast, break limits"),
    ("kv", "contact", "linkedin.com/in/raj-bhadane-45a319399"),
    ("prompt", f"{USERNAME}@github ~ $ _", None),
]

WIDTH = 490
HEIGHT = PAD_TOP + LINE_HEIGHT * len(LINES) + 20
STAGGER = 0.18
DURATION = 0.4


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render() -> str:
    rows = []
    for i, (kind, a, b) in enumerate(LINES):
        y = PAD_TOP + i * LINE_HEIGHT
        delay = i * STAGGER
        if kind == "prompt":
            text = f'<tspan fill="{ACCENT}">$</tspan> <tspan fill="{FG}">{esc(a)}</tspan>'
        elif kind == "rule":
            text = f'<tspan fill="{DIM}">{esc(a)}</tspan>'
        else:
            text = f'<tspan fill="{DIM}">{esc(a)}:</tspan> <tspan fill="{FG}">{esc(b)}</tspan>'
        rows.append(
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="14.5" '
            f'class="line" style="animation-delay:{delay:.2f}s">{text}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <style>
    .frame {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .line {{
      opacity: 0;
      transform: translateX(-8px);
      animation-name: appear;
      animation-duration: {DURATION}s;
      animation-timing-function: ease-out;
      animation-fill-mode: forwards;
    }}
    @keyframes appear {{
      0%   {{ opacity: 0; transform: translateX(-8px); }}
      100% {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
  <rect class="frame" x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8" ry="8" />
  {''.join(rows)}
</svg>
"""


def main() -> None:
    OUT_PATH.write_text(render())
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
