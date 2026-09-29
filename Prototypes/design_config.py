from pathlib import Path


# ============================================================
# EVENT DESIGN
# ============================================================

EVENT_NAME = "Netvember 2026 Celebration"
EVENT_SUBTITLE = ""
BOTTOM_TEXT = "Still Motion Archives"


# ============================================================
# GRAPHIC PANEL COLORS
# ============================================================

GRAPHIC_BACKGROUND = (245, 245, 245)
EVENT_TEXT_COLOR = (20, 20, 20)
SUBTITLE_TEXT_COLOR = (70, 70, 70)
BOTTOM_TEXT_COLOR = (90, 90, 90)


# ============================================================
# ENTIRE COLLAGE BACKGROUND
# ============================================================

COLLAGE_BACKGROUND_STYLE = "solid"
COLLAGE_BACKGROUND_COLOR = (255, 255, 255)

COLLAGE_GRADIENT_START = (255, 255, 255)
COLLAGE_GRADIENT_END = (220, 220, 220)
COLLAGE_GRADIENT_DIRECTION = "horizontal"

# Optional full-canvas background image.
# When COLLAGE_BACKGROUND_STYLE == "image", this image is
# fitted to the entire 1800 x 1200 collage.
BACKGROUND_IMAGE = Path(r"C:\Photobooth\Photos\Designs\collage_background.png")


# ============================================================
# FONTS
# ============================================================

EVENT_FONT = Path(r"C:\Windows\Fonts\arialbd.ttf")
SUBTITLE_FONT = Path(r"C:\Windows\Fonts\arial.ttf")
BOTTOM_FONT = Path(r"C:\Windows\Fonts\arial.ttf")


# ============================================================
# FONT SIZES / TEXT POSITIONS
# ============================================================

EVENT_FONT_SIZE_PERCENT = 0.09
SUBTITLE_FONT_SIZE_PERCENT = 0.045
BOTTOM_FONT_SIZE_PERCENT = 0.035

EVENT_NAME_TOP_PERCENT = 0.08
SUBTITLE_TOP_PERCENT = 0.21
BOTTOM_TEXT_TOP_PERCENT = 0.88


# ============================================================
# COLLAGE SETTINGS
# Keep these unchanged: they define the working fixed layout.
# ============================================================

CANVAS_WIDTH = 1800
CANVAS_HEIGHT = 1200
MARGIN = 50
GAP = 25
PRINT_DPI = 300


# ============================================================
# FILE LOCATIONS
# ============================================================

PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")
PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)

COLLAGE_FILENAME = "latest_collage.jpg"
OUTPUT_FILE = PHOTO_FOLDER / COLLAGE_FILENAME

DESIGN_FOLDER = PHOTO_FOLDER / "Designs"
DESIGN_FOLDER.mkdir(parents=True, exist_ok=True)

DESIGN_LAYOUT_FILE = DESIGN_FOLDER / "design_layout.json"


# ============================================================
# DESIGN ELEMENTS
#
# x, y, width and height are normalized against the complete
# 1800 x 1200 canvas. rotation is stored in degrees.
# z_index controls front/back ordering.
# ============================================================

DESIGN_ELEMENTS = []


# ============================================================
# LEGACY SINGLE-GRAPHIC SETTINGS
# Kept only for compatibility with older project code.
# collage.py below does not use these for the new editor.
# ============================================================

GRAPHIC_IMAGE = DESIGN_FOLDER / "event_logo.png"
GRAPHIC_MAX_WIDTH_PERCENT = 0.75
GRAPHIC_MAX_HEIGHT_PERCENT = 0.50
GRAPHIC_TOP_PERCENT = 0.32
