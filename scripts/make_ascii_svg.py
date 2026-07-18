#!/usr/bin/env python3
"""Local-only: convert prepped-photo.png into a self-typing ASCII SVG portrait.

Each row wipes in left-to-right via a clip-path animation, staggered
top-to-bottom, then freezes. Monospace, single accent color, no images.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "prepped-photo.png"
OUT = ROOT / "avi-ascii.svg"

RAMP = " .`:-=+*cs#%@"  # sparse (bright) -> dense (dark)
COLS = 74
CELL_W = 5.6
CELL_H = 10.5  # monospace rows are taller than wide
CHAR_ASPECT = CELL_W / CELL_H  # corrects sampling grid for non-square cells
BUST_FRAC = 0.5  # keep only the top half of the subject's bounding box (head+shoulders)
PAD_FRAC = 0.06  # padding around the crop, as a fraction of the crop's own size


def crop_to_bust(im: Image.Image) -> Image.Image:
    arr = np.asarray(im.convert("RGB")).astype(np.int16)
    is_bg = np.all(arr > 245, axis=2)
    fg_rows = np.where(~np.all(is_bg, axis=1))[0]
    fg_cols = np.where(~np.all(is_bg, axis=0))[0]
    if fg_rows.size == 0 or fg_cols.size == 0:
        return im

    top, bottom = fg_rows[0], fg_rows[-1]
    left, right = fg_cols[0], fg_cols[-1]
    bust_bottom = top + int((bottom - top) * BUST_FRAC)

    h = bust_bottom - top
    w = right - left
    pad_h = int(h * PAD_FRAC)
    pad_w = int(w * PAD_FRAC)

    y0 = max(0, top - pad_h)
    y1 = min(im.height, bust_bottom + pad_h)
    x0 = max(0, left - pad_w)
    x1 = min(im.width, right + pad_w)
    return im.crop((x0, y0, x1, y1))

FG = "#c9d1d9"
BG = "#0d1117"
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
ROW_STAGGER = 0.045
WIPE_DURATION = 0.28


def to_ascii_rows(im: Image.Image) -> list[str]:
    w, h = im.size
    rows = max(1, round(COLS * (h / w) * CHAR_ASPECT))
    small = im.convert("L").resize((COLS, rows), Image.LANCZOS)
    arr = np.asarray(small).astype(np.float32) / 255.0

    ramp_idx = (1.0 - arr) * (len(RAMP) - 1)  # bright -> sparse char
    ramp_idx = np.clip(ramp_idx, 0, len(RAMP) - 1).round().astype(int)

    lines = []
    for r in range(rows):
        lines.append("".join(RAMP[i] for i in ramp_idx[r]))
    return lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", " ")


def render(lines: list[str]) -> str:
    width = COLS * CELL_W
    height = len(lines) * CELL_H
    clip_defs = []
    texts = []

    for r, line in enumerate(lines):
        y = (r + 1) * CELL_H - 2
        clip_id = f"wipe{r}"
        delay = r * ROW_STAGGER
        clip_defs.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{r * CELL_H}" width="0" height="{CELL_H + 1}" '
            f'class="wipe" style="animation-delay:{delay:.3f}s"/></clipPath>'
        )
        texts.append(
            f'<text x="0" y="{y}" font-family="{FONT}" font-size="{CELL_H - 1.5}" '
            f'fill="{FG}" clip-path="url(#{clip_id})" xml:space="preserve">{esc(line)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" width="{width:.1f}" height="{height:.1f}">
  <defs>
    {''.join(clip_defs)}
  </defs>
  <style>
    .bg {{ fill: {BG}; }}
    .wipe {{
      animation-name: wipe-in;
      animation-duration: {WIPE_DURATION}s;
      animation-timing-function: steps(24, end);
      animation-fill-mode: forwards;
    }}
    @keyframes wipe-in {{
      from {{ width: 0; }}
      to   {{ width: {width:.1f}px; }}
    }}
  </style>
  <rect class="bg" x="0" y="0" width="{width:.1f}" height="{height:.1f}" />
  {''.join(texts)}
</svg>
"""


def main() -> None:
    if not SRC.exists():
        sys.exit(f"Missing {SRC} — run prep_photo.py first.")
    im = crop_to_bust(Image.open(SRC))
    lines = to_ascii_rows(im)
    OUT.write_text(render(lines))
    print(f"Wrote {OUT} ({len(lines)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()
