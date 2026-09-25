# --------------------------------------------------------------
# collage.py
# --------------------------------------------------------------
# Build a 4×6‑inch (300 dpi) 2×2 collage from four JPEG files.
# --------------------------------------------------------------

from pathlib import Path
from typing import List

from PIL import Image, ImageOps

# ------------------------------------------------------------------
# SETTINGS – adjust here if you ever need a different size/DPI
# ------------------------------------------------------------------
INCHES_W, INCHES_H = 6, 4          # final print size (landscape) in inches
DPI = 300                         # printer quality – 300 dpi is standard
CANVAS_W_PX = INCHES_W * DPI       # 1800 px
CANVAS_H_PX = INCHES_H * DPI       # 1200 px
MARGIN_PX = 30                     # white border around each thumbnail


def _prepare_thumb(img_path: Path) -> Image.Image:
    """
    Open an image, resize it while preserving its aspect ratio,
    then centre it on a white square that is exactly half of the final canvas
    (900 × 900 px for a 6×4‑in canvas).

    Returns the ready‑to‑paste thumbnail as a Pillow ``Image`` object.
    """
    # Size of each quadrant of the final canvas
    thumb_w = CANVAS_W_PX // 2   # 900
    thumb_h = CANVAS_H_PX // 2   # 600 → we keep both dimensions equal for a square
    usable_w = thumb_w - 2 * MARGIN_PX
    usable_h = thumb_h - 2 * MARGIN_PX

    # Load and convert to a consistent mode (RGB)
    img = Image.open(img_path).convert("RGB")

    # Resize while preserving aspect ratio, then pad to the usable size
    img_resized = ImageOps.pad(img, (usable_w, usable_h), color="white", centering=(0.5, 0.5))

    # Put the resized image onto a clean white canvas that includes the margin
    canvas = Image.new("RGB", (thumb_w, thumb_h), "white")
    canvas.paste(img_resized, (MARGIN_PX, MARGIN_PX))

    return canvas


def make_collage(image_paths: List[Path]) -> Path:
    """
    Create a printable 4×6‑inch collage from *exactly four* JPEG files.

    Parameters
    ----------
    image_paths: List[Path]
        Four pathlib ``Path`` objects pointing to the source photos.
        The list may be unsorted – the function will sort by creation time
        (oldest → newest) so the layout is predictable.

    Returns
    -------
    Path
        Path to the saved collage file (``photobooth_collage.jpg``)
        placed in the same directory as the source images.
    """
    if len(image_paths) != 4:
        raise ValueError("make_collage requires exactly four image paths.")

    # ------------------------------------------------------------------
    # 1️⃣ Sort pictures by creation‑time (oldest first) for a stable layout
    # ------------------------------------------------------------------
    sorted_paths = sorted(image_paths, key=lambda p: p.stat().st_ctime)

    # ------------------------------------------------------------------
    # 2️⃣ Build the 4 thumbnails (900×900 each)
    # ------------------------------------------------------------------
    thumbs = [_prepare_thumb(p) for p in sorted_paths]

    # ------------------------------------------------------------------
    # 3️⃣ Create the final canvas (1800×1200 px) and embed thumbnails
    # ------------------------------------------------------------------
    collage = Image.new("RGB", (CANVAS_W_PX, CANVAS_H_PX), "white")
    collage.info["dpi"] = (DPI, DPI)   # store DPI metadata – many printers read it

    # Positions of the 2×2 grid (top‑left, top‑right, bottom‑left, bottom‑right)
    positions = [
        (0, 0),                                 # top‑left
        (CANVAS_W_PX // 2, 0),                  # top‑right
        (0, CANVAS_H_PX // 2),                  # bottom‑left
        (CANVAS_W_PX // 2, CANVAS_H_PX // 2),   # bottom‑right
    ]

    for thumb, position in zip(thumbs, positions):
        collage.paste(thumb, position)

    output_path = sorted_paths[0].parent / "photobooth_collage.jpg"
    collage.save(output_path, "JPEG", dpi=(DPI, DPI), quality=95)

    return output_path