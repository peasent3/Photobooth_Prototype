# --------------------------------------------------------------
# collage.py
# --------------------------------------------------------------
# Helper utilities for creating a 4×6‑inch (300 dpi) collage
# from four JPEG images taken with the photobooth.
#
# Usage example (inside app.py or a REPL):
#
#   from collage import create_latest_collage
#   collage_path = create_latest_collage()   # → Path to photobooth_collage.jpg
#
# --------------------------------------------------------------

from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageOps

# ----------------------------------------------------------------------
# Configuration – adjust only if you want a different size/DPI
# ----------------------------------------------------------------------
INCHES_W, INCHES_H = 6, 4          # final print size (landscape) in inches
DPI = 300                         # printer quality – 300 dpi is standard
CANVAS_W_PX = INCHES_W * DPI       # 1800 px
CANVAS_H_PX = INCHES_H * DPI       # 1200 px
MARGIN_PX = 30                     # white border around each thumbnail

# The default folder where the camera stores pictures.
# Keep it in sync with the constant you use in camera.py.
PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")
PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)


def get_last_n_photos(folder: Path, n: int = 4) -> List[Path]:
    """
    Return the *n* most‑recent JPEG files (by creation‑time) that exist
    inside ``folder``.  If there are fewer than ``n`` files an empty list
    is returned.

    Parameters
    ----------
    folder : pathlib.Path
        Directory that contains the pictures.
    n : int, default 4
        How many recent files you want.

    Returns
    -------
    list[Path]
        List of paths ordered from oldest → newest (so the collage layout
        follows the order the pictures were taken).
    """
    jpeg_files = sorted(
        folder.glob("*.jpg"),
        key=lambda p: p.stat().st_ctime,   # creation time
        reverse=True                        # newest first
    )
    if len(jpeg_files) < n:
        return []      # not enough photos yet
    # Take the newest *n* and then reverse so the order is oldest→newest
    return list(reversed(jpeg_files[:n]))


def _prepare_thumbnail(img_path: Path) -> Image.Image:
    """
    Open ``img_path`` and return a 900 × 900 px square thumbnail that
    contains the picture centred on a white background.

    The thumbnail size (900 × 900) is exactly half of the final canvas
    (1800 × 1200) – the extra space (margin) is added later.
    """
    thumb_w = CANVAS_W_PX // 2   # 900
    thumb_h = CANVAS_H_PX // 2   # 600 → we treat both dimensions as a square
    usable_w = thumb_w - 2 * MARGIN_PX
    usable_h = thumb_h - 2 * MARGIN_PX

    img = Image.open(img_path).convert("RGB")
    # Resize while preserving aspect ratio, then pad to the usable size
    img_resized = ImageOps.pad(
        img,
        (usable_w, usable_h),
        color="white",
        centering=(0.5, 0.5)
    )
    # Paste onto a clean white square that includes the margin
    canvas = Image.new("RGB", (thumb_w, thumb_h), "white")
    canvas.paste(img_resized, (MARGIN_PX, MARGIN_PX))
    return canvas


def make_collage(photo_paths: List[Path],
                 output_path: Optional[Path] = None) -> Path:
    """
    Build a 4 × 6‑inch collage from *exactly four* JPEG files.

    Parameters
    ----------
    photo_paths : list[Path]
        Four image paths (oldest first → newest last).  The function will
        raise ``ValueError`` if the list length is not four.
    output_path : Path or None
        Where to save the collage.  If omitted the file
        ``photobooth_collage.jpg`` is created inside the same folder as
        the source photos.

    Returns
    -------
    pathlib.Path
        The path of the saved JPEG collage.
    """
    if len(photo_paths) != 4:
        raise ValueError("make_collage expects exactly four image paths.")

    # ------------------------------------------------------------------
    # 1️⃣ Build the 4 thumbnails (900 × 900 each)
    # ------------------------------------------------------------------
    thumbs = [_prepare_thumbnail(p) for p in photo_paths]

    # ------------------------------------------------------------------
    # 2️⃣ Create the final canvas (1800 × 1200 @ 300 dpi)
    # ------------------------------------------------------------------
    collage = Image.new("RGB", (CANVAS_W_PX, CANVAS_H_PX), "white")
    collage.info["dpi"] = (DPI, DPI)   # store DPI metadata – many printers read it

    # Positions of the 2 × 2 grid (top‑left, top‑right, bottom‑left, bottom‑right)
    positions = [
        (0, 0),                                 # top‑left
        (CANVAS_W_PX // 2, 0),                  # top‑right
        (0, CANVAS_H_PX // 2),                  # bottom‑left
        (CANVAS_W_PX // 2, CANVAS_H_PX // 2),   # bottom‑right
    ]

    for thumb, pos in zip(thumbs, positions):
        collage.paste(thumb, pos)

    # ------------------------------------------------------------------
    # 3️⃣ Determine where to write the file
    # ------------------------------------------------------------------
    if output_path is None:
        # Save next to the source photos, same folder as the first image
        output_path = photo_paths[0].parent / "photobooth_collage.jpg"

    collage.save(
        output_path,
        format="JPEG",
        quality=95,               # high‑quality JPEG with reasonable size
        dpi=(DPI, DPI),
    )
    print(f"[COLLAGE] Saved → {output_path}")
    return output_path


def create_latest_collage(folder: Path = PHOTO_FOLDER) -> Path:
    """
    Convenience helper – grabs the four newest JPEGs in *folder*,
    builds the collage and returns the path to the saved file.

    Raises
    ------
    RuntimeError
        If fewer than four photos exist in the folder.
    """
    latest = get_last_n_photos(folder, n=4)
    if len(latest) != 4:
        raise RuntimeError(
            f"Not enough photos to build a collage – need 4, found {len(latest)}."
        )
    return make_collage(latest)


# ----------------------------------------------------------------------
# If you run this file directly (python collage.py) it will attempt to
# create a collage from the latest four photos in the default folder.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        result = create_latest_collage()
        print(f"Collage created: {result}")
    except Exception as exc:
        print(f"Failed to create collage: {exc}")