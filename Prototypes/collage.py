from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import design_config


# ============================================================
# CONFIGURATION
# ============================================================

PHOTO_FOLDER = design_config.PHOTO_FOLDER

OUTPUT_FILE = design_config.OUTPUT_FILE

CANVAS_WIDTH = design_config.CANVAS_WIDTH

CANVAS_HEIGHT = design_config.CANVAS_HEIGHT

MARGIN = design_config.MARGIN

GAP = design_config.GAP


# ============================================================
# FONT LOADING
# ============================================================

def get_font(font_path, size):

    font_path = Path(font_path)

    if font_path.exists():

        try:

            return ImageFont.truetype(
                str(font_path),
                size
            )

        except Exception:

            pass

    return ImageFont.load_default()


# ============================================================
# FIT IMAGE
# ============================================================

def fit_image(image, size):

    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )


# ============================================================
# CREATE COLLAGE BACKGROUND
# ============================================================

def create_collage_background(width, height):

    style = (
        design_config.COLLAGE_BACKGROUND_STYLE
        .lower()
    )


    # ========================================================
    # SOLID
    # ========================================================

    if style == "solid":

        return Image.new(
            "RGB",
            (width, height),
            design_config.COLLAGE_BACKGROUND_COLOR
        )


    # ========================================================
    # GRADIENT
    # ========================================================

    if style == "gradient":

        start_color = (
            design_config.COLLAGE_GRADIENT_START
        )

        end_color = (
            design_config.COLLAGE_GRADIENT_END
        )

        direction = (
            design_config.COLLAGE_GRADIENT_DIRECTION
            .lower()
        )


        background = Image.new(
            "RGB",
            (width, height)
        )

        draw = ImageDraw.Draw(
            background
        )


        # ====================================================
        # HORIZONTAL
        # ====================================================

        if direction == "horizontal":

            for x in range(width):

                position = (
                    x /
                    max(width - 1, 1)
                )

                color = tuple(
                    int(
                        start_color[i]
                        +
                        (
                            end_color[i]
                            -
                            start_color[i]
                        )
                        *
                        position
                    )
                    for i in range(3)
                )

                draw.line(
                    [
                        (x, 0),
                        (x, height)
                    ],
                    fill=color
                )


        # ====================================================
        # VERTICAL
        # ====================================================

        elif direction == "vertical":

            for y in range(height):

                position = (
                    y /
                    max(height - 1, 1)
                )

                color = tuple(
                    int(
                        start_color[i]
                        +
                        (
                            end_color[i]
                            -
                            start_color[i]
                        )
                        *
                        position
                    )
                    for i in range(3)
                )

                draw.line(
                    [
                        (0, y),
                        (width, y)
                    ],
                    fill=color
                )


        # ====================================================
        # DIAGONAL
        # ====================================================

        elif direction == "diagonal":

            for y in range(height):

                position_y = (
                    y /
                    max(height - 1, 1)
                )

                for x in range(width):

                    position_x = (
                        x /
                        max(width - 1, 1)
                    )

                    position = (
                        position_x +
                        position_y
                    ) / 2

                    color = tuple(
                        int(
                            start_color[i]
                            +
                            (
                                end_color[i]
                                -
                                start_color[i]
                            )
                            *
                            position
                        )
                        for i in range(3)
                    )

                    draw.point(
                        (x, y),
                        fill=color
                    )


        else:

            return Image.new(
                "RGB",
                (width, height),
                start_color
            )


        return background


    # ========================================================
    # UNKNOWN STYLE
    # ========================================================

    return Image.new(
        "RGB",
        (width, height),
        design_config.COLLAGE_BACKGROUND_COLOR
    )


# ============================================================
# CREATE GRAPHIC PANEL
# ============================================================

def create_graphic_panel(width, height):

    panel = Image.new(
        "RGB",
        (width, height),
        design_config.GRAPHIC_BACKGROUND
    )

    draw = ImageDraw.Draw(
        panel
    )


    # ========================================================
    # EVENT NAME
    # ========================================================

    event_name = (
        design_config.EVENT_NAME
    )

    if event_name:

        font_size = int(
            width *
            design_config.EVENT_FONT_SIZE_PERCENT
        )

        font = get_font(
            design_config.EVENT_FONT,
            font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            event_name,
            font=font
        )

        text_width = (
            bbox[2] -
            bbox[0]
        )

        text_x = (
            width -
            text_width
        ) // 2

        text_y = int(
            height *
            design_config.EVENT_NAME_TOP_PERCENT
        )

        draw.text(
            (
                text_x,
                text_y
            ),
            event_name,
            fill=design_config.EVENT_TEXT_COLOR,
            font=font
        )


    # ========================================================
    # SUBTITLE
    # ========================================================

    subtitle = (
        design_config.EVENT_SUBTITLE
    )

    if subtitle:

        subtitle_font_size = int(
            width *
            design_config.SUBTITLE_FONT_SIZE_PERCENT
        )

        subtitle_font = get_font(
            design_config.SUBTITLE_FONT,
            subtitle_font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            subtitle,
            font=subtitle_font
        )

        subtitle_width = (
            bbox[2] -
            bbox[0]
        )

        subtitle_x = (
            width -
            subtitle_width
        ) // 2

        subtitle_y = int(
            height *
            design_config.SUBTITLE_TOP_PERCENT
        )

        draw.text(
            (
                subtitle_x,
                subtitle_y
            ),
            subtitle,
            fill=design_config.SUBTITLE_TEXT_COLOR,
            font=subtitle_font
        )


    # ========================================================
    # BOTTOM TEXT
    # ========================================================

    bottom_text = (
        design_config.BOTTOM_TEXT
    )

    if bottom_text:

        bottom_font_size = int(
            width *
            design_config.BOTTOM_FONT_SIZE_PERCENT
        )

        bottom_font = get_font(
            design_config.BOTTOM_FONT,
            bottom_font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            bottom_text,
            font=bottom_font
        )

        bottom_width = (
            bbox[2] -
            bbox[0]
        )

        bottom_x = (
            width -
            bottom_width
        ) // 2

        bottom_y = int(
            height *
            design_config.BOTTOM_TEXT_TOP_PERCENT
        )

        draw.text(
            (
                bottom_x,
                bottom_y
            ),
            bottom_text,
            fill=design_config.BOTTOM_TEXT_COLOR,
            font=bottom_font
        )


    return panel


# ============================================================
# PLACE DESIGN ELEMENTS
# ============================================================

def place_design_elements(canvas):

    for element in design_config.DESIGN_ELEMENTS:

        try:

            filename = element.get(
                "filename"
            )

            if not filename:
                continue


            image_path = (
                design_config.DESIGN_FOLDER /
                filename
            )


            if not image_path.exists():

                print(
                    f"Design image not found: "
                    f"{image_path}"
                )

                continue


            image = Image.open(
                image_path
            ).convert("RGBA")


            # =================================================
            # NORMALIZED POSITION
            # =================================================

            x = float(
                element.get(
                    "x",
                    0.0
                )
            )

            y = float(
                element.get(
                    "y",
                    0.0
                )
            )

            width = float(
                element.get(
                    "width",
                    0.20
                )
            )

            height = float(
                element.get(
                    "height",
                    0.20
                )
            )


            # =================================================
            # CONVERT TO PIXELS
            # =================================================

            pixel_width = max(
                1,
                int(
                    CANVAS_WIDTH *
                    width
                )
            )

            pixel_height = max(
                1,
                int(
                    CANVAS_HEIGHT *
                    height
                )
            )


            pixel_x = int(
                CANVAS_WIDTH *
                x
            )

            pixel_y = int(
                CANVAS_HEIGHT *
                y
            )


            # =================================================
            # RESIZE
            # =================================================

            image.thumbnail(
                (
                    pixel_width,
                    pixel_height
                ),
                Image.Resampling.LANCZOS
            )


            # =================================================
            # PASTE
            # =================================================

            canvas.paste(
                image,
                (
                    pixel_x,
                    pixel_y
                ),
                image
            )


            print(
                f"Placed design element: "
                f"{filename} "
                f"at ({pixel_x}, {pixel_y})"
            )


        except Exception as error:

            print(
                f"Could not place design element: "
                f"{error}"
            )


# ============================================================
# MAKE COLLAGE
# ============================================================

def make_collage(photo_paths):

    if len(photo_paths) != 3:

        raise ValueError(
            "A 3-photo collage requires exactly 3 photos."
        )


    # ========================================================
    # CREATE BACKGROUND
    # ========================================================

    canvas = create_collage_background(
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    )


    # ========================================================
    # CALCULATE PHOTO CELLS
    # ========================================================

    available_width = (
        CANVAS_WIDTH
        -
        (MARGIN * 2)
        -
        GAP
    )

    available_height = (
        CANVAS_HEIGHT
        -
        (MARGIN * 2)
        -
        GAP
    )

    cell_width = (
        available_width //
        2
    )

    cell_height = (
        available_height //
        2
    )


    # ========================================================
    # CREATE GRAPHIC PANEL
    # ========================================================

    graphic_panel = create_graphic_panel(
        cell_width,
        cell_height
    )


    # ========================================================
    # LOAD PHOTOS
    # ========================================================

    photos = []


    for photo_path in photo_paths:

        photo_path = Path(
            photo_path
        )


        if not photo_path.exists():

            raise FileNotFoundError(
                f"Photo not found: {photo_path}"
            )


        image = Image.open(
            photo_path
        ).convert("RGB")


        image = fit_image(
            image,
            (
                cell_width,
                cell_height
            )
        )


        photos.append(
            image
        )


    # ========================================================
    # PHOTO POSITIONS
    # ========================================================

    x_left = MARGIN

    x_right = (
        MARGIN
        +
        cell_width
        +
        GAP
    )

    y_top = MARGIN

    y_bottom = (
        MARGIN
        +
        cell_height
        +
        GAP
    )


    # ========================================================
    # GRAPHIC PANEL
    # ========================================================

    canvas.paste(
        graphic_panel,
        (
            x_left,
            y_top
        )
    )


    # ========================================================
    # PHOTO 1
    # ========================================================

    canvas.paste(
        photos[0],
        (
            x_right,
            y_top
        )
    )


    # ========================================================
    # PHOTO 2
    # ========================================================

    canvas.paste(
        photos[1],
        (
            x_left,
            y_bottom
        )
    )


    # ========================================================
    # PHOTO 3
    # ========================================================

    canvas.paste(
        photos[2],
        (
            x_right,
            y_bottom
        )
    )


    # ========================================================
    # DESIGN ELEMENTS
    #
    # IMPORTANT:
    #
    # These are placed AFTER the photos.
    #
    # This means the uploaded graphics appear on top
    # of the collage.
    # ========================================================

    place_design_elements(
        canvas
    )


    # ========================================================
    # SAVE
    # ========================================================

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
        f"3-photo collage created: "
        f"{OUTPUT_FILE}"
    )


    return OUTPUT_FILE