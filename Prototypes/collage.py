from pathlib import Path

from PIL import Image, ImageOps


PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")

# Canon SELPHY 4x6 paper
DPI = 300

# 6 x 4 inches at 300 DPI
CANVAS_WIDTH = 1800
CANVAS_HEIGHT = 1200

# Overall outer margin
OUTER_MARGIN = 30

# Gap between photos
PHOTO_GAP = 20

BACKGROUND_COLOR = "white"


def get_last_n_photos(n=4):

    photos = list(
        PHOTO_FOLDER.glob("*.jpg")
    )

    photos.sort(
        key=lambda p: p.stat().st_ctime
    )

    return photos[-n:]


def _prepare_photo(image_path, width, height):

    image = Image.open(image_path).convert("RGB")

    # Crop the photo to exactly fill its space
    image = ImageOps.fit(
        image,
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )

    return image


def make_collage(
    photo_paths,
    output_path=None
):

    if len(photo_paths) != 4:

        raise ValueError(
            "Exactly 4 photos are required."
        )


    # ========================================================
    # Calculate photo dimensions
    # ========================================================

    available_width = (
        CANVAS_WIDTH
        - (OUTER_MARGIN * 2)
        - PHOTO_GAP
    )

    available_height = (
        CANVAS_HEIGHT
        - (OUTER_MARGIN * 2)
        - PHOTO_GAP
    )

    photo_width = available_width // 2
    photo_height = available_height // 2


    # ========================================================
    # Create 6x4 canvas
    # ========================================================

    canvas = Image.new(
        "RGB",
        (
            CANVAS_WIDTH,
            CANVAS_HEIGHT
        ),
        BACKGROUND_COLOR
    )


    # ========================================================
    # Photo positions
    # ========================================================

    x1 = OUTER_MARGIN

    x2 = (
        OUTER_MARGIN
        + photo_width
        + PHOTO_GAP
    )

    y1 = OUTER_MARGIN

    y2 = (
        OUTER_MARGIN
        + photo_height
        + PHOTO_GAP
    )


    positions = [
        (x1, y1),
        (x2, y1),
        (x1, y2),
        (x2, y2)
    ]


    # ========================================================
    # Add photos
    # ========================================================

    for photo_path, position in zip(
        photo_paths,
        positions
    ):

        photo = _prepare_photo(
            photo_path,
            photo_width,
            photo_height
        )

        canvas.paste(
            photo,
            position
        )


    # ========================================================
    # Save
    # ========================================================

    if output_path is None:

        output_path = (
            PHOTO_FOLDER
            / "photobooth_collage.jpg"
        )

    output_path = Path(output_path)


    canvas.save(
        output_path,
        "JPEG",
        quality=95,
        dpi=(DPI, DPI)
    )


    print(
        f"Collage saved: {output_path}"
    )

    print(
        f"Image size: "
        f"{CANVAS_WIDTH} x {CANVAS_HEIGHT}"
    )

    print(
        "Physical size: "
        "6 x 4 inches at 300 DPI"
    )

    return output_path


def create_latest_collage():

    photos = get_last_n_photos(4)

    if len(photos) != 4:

        raise ValueError(
            f"Need 4 photos, found {len(photos)}."
        )

    return make_collage(photos)


if __name__ == "__main__":

    create_latest_collage()