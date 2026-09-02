#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

Full pipeline (if rembg + opencv are installed):
  1. remove the background with rembg
  2. boost local contrast with CLAHE
  3. composite onto pure white

Graceful fallback (placeholder mode): PIL-only autocontrast, no background
removal. Install the extras for best results with real photos:
    pip install rembg opencv-python
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/prep_photo.py <photo> [output.png]")
        sys.exit(1)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets" / "source-prepped.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert("RGB")

    # 1. background removal (optional extra)
    try:
        from rembg import remove

        img = remove(img)
        print("[prep] background removed with rembg")
    except ImportError:
        print("[prep] rembg not installed -> keeping background")

    # flatten onto pure white so the background maps to the blank end of the ramp
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")

    gray = ImageOps.grayscale(img)

    # 2. local contrast: CLAHE via OpenCV when available, PIL autocontrast otherwise
    try:
        import cv2
        import numpy as np

        arr = np.array(gray)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = Image.fromarray(clahe.apply(arr))
        print("[prep] CLAHE contrast boost applied")
    except ImportError:
        gray = ImageOps.autocontrast(gray, cutoff=1)
        print("[prep] OpenCV not installed -> PIL autocontrast fallback")

    gray.save(out)
    print(f"[prep] wrote {out}")


if __name__ == "__main__":
    main()
