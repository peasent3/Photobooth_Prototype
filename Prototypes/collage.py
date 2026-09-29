from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import design_config


PHOTO_FOLDER = design_config.PHOTO_FOLDER
OUTPUT_FILE = design_config.OUTPUT_FILE
CANVAS_WIDTH = design_config.CANVAS_WIDTH
CANVAS_HEIGHT = design_config.CANVAS_HEIGHT
MARGIN = design_config.MARGIN
GAP = design_config.GAP


def get_font(font_path, size):
    font_path = Path(font_path)

    if font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), max(1, int(size)))
        except Exception:
            pass

    return ImageFont.load_default()


def fit_image(image, size):
    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )


def create_collage_background(width, height):
    style = str(design_config.COLLAGE_BACKGROUND_STYLE).lower()

    if style == "solid":
        return Image.new(
            "RGB",
            (width, height),
            design_config.COLLAGE_BACKGROUND_COLOR
        )

    if style == "image":
        image_path = Path(design_config.BACKGROUND_IMAGE)
        if image_path.exists():
            with Image.open(image_path) as source:
                image = source.convert("RGB")
            return ImageOps.fit(
                image,
                (width, height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5)
            )
        return Image.new(
            "RGB",
            (width, height),
            design_config.COLLAGE_BACKGROUND_COLOR
        )

    if style != "gradient":
        return Image.new(
            "RGB",
            (width, height),
            design_config.COLLAGE_BACKGROUND_COLOR
        )

    start_color = design_config.COLLAGE_GRADIENT_START
    end_color = design_config.COLLAGE_GRADIENT_END
    direction = str(design_config.COLLAGE_GRADIENT_DIRECTION).lower()

    background = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(background)

    if direction == "horizontal":
        for x in range(width):
            position = x / max(width - 1, 1)
            color = tuple(
                int(start_color[i] + (end_color[i] - start_color[i]) * position)
                for i in range(3)
            )
            draw.line([(x, 0), (x, height)], fill=color)

    elif direction == "vertical":
        for y in range(height):
            position = y / max(height - 1, 1)
            color = tuple(
                int(start_color[i] + (end_color[i] - start_color[i]) * position)
                for i in range(3)
            )
            draw.line([(0, y), (width, y)], fill=color)

    elif direction == "diagonal":
        # Faster diagonal gradient: draw horizontal lines whose midpoint
        # approximates the same diagonal interpolation used by the editor.
        for y in range(height):
            y_pos = y / max(height - 1, 1)
            left_pos = y_pos / 2
            right_pos = (1 + y_pos) / 2

            left_color = tuple(
                int(start_color[i] + (end_color[i] - start_color[i]) * left_pos)
                for i in range(3)
            )
            right_color = tuple(
                int(start_color[i] + (end_color[i] - start_color[i]) * right_pos)
                for i in range(3)
            )

            # Build one scanline with interpolation.
            line = Image.new("RGB", (width, 1))
            pixels = line.load()
            for x in range(width):
                t = x / max(width - 1, 1)
                pixels[x, 0] = tuple(
                    int(left_color[i] + (right_color[i] - left_color[i]) * t)
                    for i in range(3)
                )
            background.paste(line, (0, y))

    else:
        return Image.new("RGB", (width, height), start_color)

    return background


def create_graphic_panel(width, height):
    # The top-left area is part of the same full collage canvas.
    # Gradient and image backgrounds therefore show through it.
    if design_config.COLLAGE_BACKGROUND_STYLE.lower() in ("gradient", "image"):
        panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    else:
        panel = Image.new(
            "RGBA",
            (width, height),
            (*design_config.GRAPHIC_BACKGROUND, 255)
        )
    draw = ImageDraw.Draw(panel)

    event_name = design_config.EVENT_NAME
    if event_name:
        font_size = int(width * design_config.EVENT_FONT_SIZE_PERCENT)
        font = get_font(design_config.EVENT_FONT, font_size)
        bbox = draw.textbbox((0, 0), event_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = int(height * design_config.EVENT_NAME_TOP_PERCENT)
        draw.text(
            (text_x, text_y),
            event_name,
            fill=design_config.EVENT_TEXT_COLOR,
            font=font
        )

    subtitle = design_config.EVENT_SUBTITLE
    if subtitle:
        font_size = int(width * design_config.SUBTITLE_FONT_SIZE_PERCENT)
        font = get_font(design_config.SUBTITLE_FONT, font_size)
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = int(height * design_config.SUBTITLE_TOP_PERCENT)
        draw.text(
            (text_x, text_y),
            subtitle,
            fill=design_config.SUBTITLE_TEXT_COLOR,
            font=font
        )

    bottom_text = design_config.BOTTOM_TEXT
    if bottom_text:
        font_size = int(width * design_config.BOTTOM_FONT_SIZE_PERCENT)
        font = get_font(design_config.BOTTOM_FONT, font_size)
        bbox = draw.textbbox((0, 0), bottom_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = int(height * design_config.BOTTOM_TEXT_TOP_PERCENT)
        draw.text(
            (text_x, text_y),
            bottom_text,
            fill=design_config.BOTTOM_TEXT_COLOR,
            font=font
        )

    return panel


def place_design_elements(canvas):
    elements = sorted(
        design_config.DESIGN_ELEMENTS,
        key=lambda item: int(item.get("z_index", 0))
    )

    for element in elements:
        try:
            filename = Path(str(element.get("filename", ""))).name
            if not filename:
                continue

            image_path = design_config.DESIGN_FOLDER / filename
            if not image_path.exists():
                print(f"Design image not found: {image_path}")
                continue

            image = Image.open(image_path).convert("RGBA")

            x = float(element.get("x", 0.05))
            y = float(element.get("y", 0.05))
            width = float(element.get("width", 0.20))
            height = float(element.get("height", 0.20))
            rotation = float(element.get("rotation", 0))

            pixel_width = max(1, int(CANVAS_WIDTH * width))
            pixel_height = max(1, int(CANVAS_HEIGHT * height))
            pixel_x = int(CANVAS_WIDTH * x)
            pixel_y = int(CANVAS_HEIGHT * y)

            # Match the editor's rectangular design box exactly.
            image = image.resize(
                (pixel_width, pixel_height),
                Image.Resampling.LANCZOS
            )

            if rotation:
                image = image.rotate(
                    -rotation,
                    resample=Image.Resampling.BICUBIC,
                    expand=True
                )

                # Keep rotation centered around the unrotated design box.
                pixel_x -= (image.width - pixel_width) // 2
                pixel_y -= (image.height - pixel_height) // 2

            canvas_rgba = canvas.convert("RGBA")
            canvas_rgba.alpha_composite(image, (pixel_x, pixel_y))
            canvas.paste(canvas_rgba.convert("RGB"))

        except Exception as error:
            print(f"Could not place design element: {error}")


def make_collage(photo_paths):
    if len(photo_paths) != 3:
        raise ValueError(
            "A 3-photo collage requires exactly 3 photos."
        )

    canvas = create_collage_background(
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    )

    available_width = (
        CANVAS_WIDTH
        - (MARGIN * 2)
        - GAP
    )

    available_height = (
        CANVAS_HEIGHT
        - (MARGIN * 2)
        - GAP
    )

    cell_width = available_width // 2
    cell_height = available_height // 2

    graphic_panel = create_graphic_panel(
        cell_width,
        cell_height
    )

    photos = []

    for photo_path in photo_paths:
        photo_path = Path(photo_path)

        if not photo_path.exists():
            raise FileNotFoundError(
                f"Photo not found: {photo_path}"
            )

        image = Image.open(photo_path).convert("RGB")
        image = fit_image(
            image,
            (cell_width, cell_height)
        )
        photos.append(image)

    # These are the same fixed positions as your original collage.py.
    x_left = MARGIN
    x_right = MARGIN + cell_width + GAP
    y_top = MARGIN
    y_bottom = MARGIN + cell_height + GAP

    # Top-left design/text panel.
    canvas.paste(
        graphic_panel,
        (x_left, y_top),
        graphic_panel
    )

    # Photo 1: fixed top-right.
    canvas.paste(
        photos[0],
        (x_right, y_top)
    )

    # Photo 2: fixed bottom-left.
    canvas.paste(
        photos[1],
        (x_left, y_bottom)
    )

    # Photo 3: fixed bottom-right.
    canvas.paste(
        photos[2],
        (x_right, y_bottom)
    )

    # Movable design images are overlays. Photos themselves never move.
    place_design_elements(canvas)

    canvas.save(
        OUTPUT_FILE,
        "JPEG",
        quality=95,
        dpi=(
            design_config.PRINT_DPI,
            design_config.PRINT_DPI
        )
    )

    print(
        f"3-photo collage created: {OUTPUT_FILE}"
    )

    return OUTPUT_FILE
