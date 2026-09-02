#!/usr/bin/env python3
"""Generate a placeholder portrait (assets/placeholder-photo.png).

A PIL-drawn head-and-shoulders silhouette with soft shading — enough
structure for the ASCII pipeline to produce a readable face. Delete this
and run prep_photo.py on your real photo when ready.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "placeholder-photo.png"
W, H = 600, 640


def main() -> None:
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)

    cx = W // 2
    # shoulders / torso
    d.ellipse([cx - 210, 400, cx + 210, 900], fill=60)
    # neck
    d.rectangle([cx - 45, 330, cx + 45, 440], fill=95)
    # head
    d.ellipse([cx - 130, 90, cx + 130, 380], fill=130)

    # soft shading: darker right side, highlight left — gives CLAHE/grayscale
    # something to bite into so the ASCII ramp spans its full range
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    sd.ellipse([cx - 130, 90, cx + 130, 380], fill=0)
    sd.ellipse([cx - 40, 100, cx + 150, 400], fill=70)
    shade = shade.filter(ImageFilter.GaussianBlur(40))
    img = Image.composite(Image.new("L", (W, H), 70), img, shade.point(lambda p: p))

    hi = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hi)
    hd.ellipse([cx - 100, 130, cx - 10, 300], fill=80)
    hi = hi.filter(ImageFilter.GaussianBlur(35))
    img = Image.composite(Image.new("L", (W, H), 215), img, hi)

    img = img.filter(ImageFilter.GaussianBlur(2))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT)
    print(f"[placeholder] wrote {OUT}")


if __name__ == "__main__":
    main()
