#!/usr/bin/env python3
"""Local-only: remove background, boost contrast, composite onto white.

Run this once whenever you change source-photo.jpg. The daily CI workflow
never touches this script — only requests/beautifulsoup4 run there.
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-photo.jpg"
OUT = ROOT / "prepped-photo.png"


def remove_background(im: Image.Image) -> Image.Image:
    from rembg import remove

    buf = io.BytesIO()
    im.save(buf, format="PNG")
    cut = remove(buf.getvalue())
    return Image.open(io.BytesIO(cut)).convert("RGBA")


def boost_contrast(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGB"))
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    return Image.fromarray(rgb)


def composite_on_white(cut: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.alpha_composite(cut)
    return bg.convert("RGB")


def main() -> None:
    if not SRC.exists():
        sys.exit(f"Missing {SRC} — place your photo there first.")

    im = Image.open(SRC).convert("RGB")
    cut = remove_background(im)
    composited = composite_on_white(cut)
    final = boost_contrast(composited)
    final.save(OUT)
    print(f"Wrote {OUT} ({final.size[0]}x{final.size[1]})")


if __name__ == "__main__":
    main()
