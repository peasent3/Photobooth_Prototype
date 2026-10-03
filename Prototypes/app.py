from flask import (
    Flask,
    render_template,
    jsonify,
    Response,
    send_file,
    request
)

import json
import time
import uuid
from pathlib import Path

from PIL import Image

from camera import A7CII
from collage import make_collage
from printer import print_file
from cloud_storage import upload_session

import design_config


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Allow large full-canvas background/design uploads (50 MB).
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# ============================================================
# CAMERA / SESSION STATE
# ============================================================

camera = A7CII()

session_active = False

session_photos = []

latest_collage = None

# Contains information returned by cloud_storage.py
# after a successful upload.
latest_cloud_session = None


# ============================================================
# DESIGN STORAGE
# ============================================================

DESIGN_FOLDER = design_config.DESIGN_FOLDER

DESIGN_LAYOUT_FILE = (
    design_config.DESIGN_LAYOUT_FILE
)

DESIGN_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

ALLOWED_DESIGN_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}

BACKGROUND_IMAGE_PATH = (
    DESIGN_FOLDER
    / "collage_background.png"
)

DESIGN_SETTINGS_FILE = (
    DESIGN_FOLDER
    / "design_settings.json"
)

design_config.BACKGROUND_IMAGE = (
    BACKGROUND_IMAGE_PATH
)


# ============================================================
# COLOR HELPERS
# ============================================================

def rgb_to_hex(rgb):

    return "#{:02x}{:02x}{:02x}".format(
        rgb[0],
        rgb[1],
        rgb[2]
    )


def hex_to_rgb(hex_color):

    hex_color = str(
        hex_color
    ).lstrip("#")

    if len(hex_color) != 6:

        raise ValueError(
            "Invalid color."
        )

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


# ============================================================
# LOAD DESIGN LAYOUT
# ============================================================

def load_design_layout():

    if not DESIGN_LAYOUT_FILE.exists():

        design_config.DESIGN_ELEMENTS = []

        return

    try:

        with DESIGN_LAYOUT_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        if isinstance(
            data,
            list
        ):

            design_config.DESIGN_ELEMENTS = (
                data
            )

        else:

            design_config.DESIGN_ELEMENTS = []

    except Exception as error:

        print(
            f"Could not load design layout: "
            f"{error}"
        )

        design_config.DESIGN_ELEMENTS = []


# ============================================================
# SAVE DESIGN LAYOUT
# ============================================================

def save_design_layout():

    with DESIGN_LAYOUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            design_config.DESIGN_ELEMENTS,
            file,
            indent=4
        )


# ============================================================
# LOAD SAVED DESIGN SETTINGS
# ============================================================

def load_saved_settings():

    if not DESIGN_SETTINGS_FILE.exists():
        return

    try:

        data = json.loads(
            DESIGN_SETTINGS_FILE.read_text(
                encoding="utf-8"
            )
        )

        if "event_name" in data:

            design_config.EVENT_NAME = str(
                data["event_name"]
            )

        if "event_subtitle" in data:

            design_config.EVENT_SUBTITLE = str(
                data["event_subtitle"]
            )

        if "bottom_text" in data:

            design_config.BOTTOM_TEXT = str(
                data["bottom_text"]
            )

        if "background_color" in data:

            design_config.GRAPHIC_BACKGROUND = (
                hex_to_rgb(
                    data[
                        "background_color"
                    ]
                )
            )

        if "event_text_color" in data:

            design_config.EVENT_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "event_text_color"
                    ]
                )
            )

        if "subtitle_text_color" in data:

            design_config.SUBTITLE_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "subtitle_text_color"
                    ]
                )
            )

        if "bottom_text_color" in data:

            design_config.BOTTOM_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "bottom_text_color"
                    ]
                )
            )

        if "event_font_size" in data:

            design_config.EVENT_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "event_font_size"
                    ]
                )
            )

        if "subtitle_font_size" in data:

            design_config.SUBTITLE_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "subtitle_font_size"
                    ]
                )
            )

        if "bottom_font_size" in data:

            design_config.BOTTOM_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "bottom_font_size"
                    ]
                )
            )

        if "collage_background_style" in data:

            design_config.COLLAGE_BACKGROUND_STYLE = (
                str(
                    data[
                        "collage_background_style"
                    ]
                )
            )

        if "collage_background_color" in data:

            design_config.COLLAGE_BACKGROUND_COLOR = (
                hex_to_rgb(
                    data[
                        "collage_background_color"
                    ]
                )
            )

        if "collage_gradient_start" in data:

            design_config.COLLAGE_GRADIENT_START = (
                hex_to_rgb(
                    data[
                        "collage_gradient_start"
                    ]
                )
            )

        if "collage_gradient_end" in data:

            design_config.COLLAGE_GRADIENT_END = (
                hex_to_rgb(
                    data[
                        "collage_gradient_end"
                    ]
                )
            )

        if "collage_gradient_direction" in data:

            design_config.COLLAGE_GRADIENT_DIRECTION = (
                str(
                    data[
                        "collage_gradient_direction"
                    ]
                )
            )

    except Exception as error:

        print(
            "Could not load saved "
            f"design settings: {error}"
        )


# ============================================================
# LOAD DESIGN FILES ON STARTUP
# ============================================================

load_design_layout()

load_saved_settings()


# ============================================================
# JSON ERROR FOR OVERSIZED UPLOADS
# ============================================================

@app.errorhandler(413)
def upload_too_large(error):

    return jsonify({

        "success": False,

        "message":
            "The image is too large. "
            "Please use an image smaller "
            "than 50 MB."

    }), 413


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# DESIGN STUDIO PAGE
# ============================================================

@app.route("/design")
def design():

    return render_template(
        "design.html"
    )


# ============================================================
# GET DESIGN CONFIGURATION
# ============================================================

@app.route("/design-config")
def get_design_config():

    return jsonify({

        "event_name":
            design_config.EVENT_NAME,

        "event_subtitle":
            design_config.EVENT_SUBTITLE,

        "bottom_text":
            design_config.BOTTOM_TEXT,

        "background_color":
            rgb_to_hex(
                design_config.GRAPHIC_BACKGROUND
            ),

        "event_text_color":
            rgb_to_hex(
                design_config.EVENT_TEXT_COLOR
            ),

        "subtitle_text_color":
            rgb_to_hex(
                design_config.SUBTITLE_TEXT_COLOR
            ),

        "bottom_text_color":
            rgb_to_hex(
                design_config.BOTTOM_TEXT_COLOR
            ),

        "event_font_size":
            design_config.EVENT_FONT_SIZE_PERCENT,

        "subtitle_font_size":
            design_config.SUBTITLE_FONT_SIZE_PERCENT,

        "bottom_font_size":
            design_config.BOTTOM_FONT_SIZE_PERCENT,

        "collage_background_style":
            design_config.COLLAGE_BACKGROUND_STYLE,

        "collage_background_color":
            rgb_to_hex(
                design_config.COLLAGE_BACKGROUND_COLOR
            ),

        "collage_gradient_start":
            rgb_to_hex(
                design_config.COLLAGE_GRADIENT_START
            ),

        "collage_gradient_end":
            rgb_to_hex(
                design_config.COLLAGE_GRADIENT_END
            ),

        "collage_gradient_direction":
            design_config.COLLAGE_GRADIENT_DIRECTION,

        "background_image_exists":
            BACKGROUND_IMAGE_PATH.exists(),

        "background_image_url":
            (
                "/background-image"
                if BACKGROUND_IMAGE_PATH.exists()
                else None
            ),

        "design_elements":
            design_config.DESIGN_ELEMENTS,

        "canvas_width":
            design_config.CANVAS_WIDTH,

        "canvas_height":
            design_config.CANVAS_HEIGHT,

        "margin":
            design_config.MARGIN,

        "gap":
            design_config.GAP
    })


# ============================================================
# UPLOAD FULL-CANVAS BACKGROUND
# ============================================================

@app.route(
    "/upload-background",
    methods=["POST"]
)
@app.route(
    "/upload-background-image",
    methods=["POST"]
)
def upload_background():

    try:

        image_file = request.files.get(
            "background"
        )

        if (
            image_file is None
            or image_file.filename == ""
        ):

            return jsonify({

                "success": False,

                "message":
                    "Choose a background "
                    "image first."

            }), 400

        extension = Path(
            image_file.filename
        ).suffix.lower()

        if extension not in (
            ALLOWED_DESIGN_EXTENSIONS
        ):

            return jsonify({

                "success": False,

                "message":
                    "Only PNG, JPG and JPEG "
                    "images are allowed."

            }), 400

        # Normalize every background to PNG.

        image_file.stream.seek(
            0
        )

        with Image.open(
            image_file.stream
        ) as image:

            image.convert(
                "RGB"
            ).save(
                BACKGROUND_IMAGE_PATH,
                "PNG"
            )

        design_config.BACKGROUND_IMAGE = (
            BACKGROUND_IMAGE_PATH
        )

        design_config.COLLAGE_BACKGROUND_STYLE = (
            "image"
        )

        return jsonify({

            "success": True,

            "message":
                "Full-canvas background uploaded.",

            "url":
                "/background-image"
        })

    except Exception as error:

        print(
            f"Background upload error: "
            f"{error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# SERVE BACKGROUND IMAGE
# ============================================================

@app.route("/background-image")
def background_image():

    if not BACKGROUND_IMAGE_PATH.exists():

        return "", 404

    return send_file(
        BACKGROUND_IMAGE_PATH,
        mimetype="image/png"
    )


# ============================================================
# DELETE BACKGROUND IMAGE
# ============================================================

@app.route(
    "/delete-background",
    methods=["POST"]
)
def delete_background():

    try:

        if BACKGROUND_IMAGE_PATH.exists():

            BACKGROUND_IMAGE_PATH.unlink()

        if (
            design_config.COLLAGE_BACKGROUND_STYLE
            == "image"
        ):

            design_config.COLLAGE_BACKGROUND_STYLE = (
                "solid"
            )

        return jsonify({

            "success": True,

            "message":
                "Background image removed."
        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# UPLOAD DESIGN IMAGE
# ============================================================

@app.route(
    "/upload-design",
    methods=["POST"]
)
def upload_design():

    try:

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "message":
                    "No image was selected."

            }), 400

        image_file = request.files[
            "image"
        ]

        if image_file.filename == "":

            return jsonify({

                "success": False,

                "message":
                    "No image was selected."

            }), 400

        original_name = Path(
            image_file.filename
        ).name

        extension = Path(
            original_name
        ).suffix.lower()

        if extension not in (
            ALLOWED_DESIGN_EXTENSIONS
        ):

            return jsonify({

                "success": False,

                "message":
                    "Only JPG, JPEG and PNG "
                    "images are allowed."

            }), 400

        element_id = (
            uuid.uuid4().hex[:12]
        )

        filename = (
            f"design_{element_id}"
            f"{extension}"
        )

        save_path = (
            DESIGN_FOLDER
            / filename
        )

        image_file.save(
            save_path
        )

        next_z = 1

        if design_config.DESIGN_ELEMENTS:

            next_z = (
                max(
                    int(
                        item.get(
                            "z_index",
                            0
                        )
                    )
                    for item
                    in design_config.DESIGN_ELEMENTS
                )
                + 1
            )

        element = {

            "id":
                element_id,

            "filename":
                filename,

            "original_name":
                original_name,

            "x":
                0.08,

            "y":
                0.08,

            "width":
                0.20,

            "height":
                0.20,

            "rotation":
                0,

            "z_index":
                next_z
        }

        design_config.DESIGN_ELEMENTS.append(
            element
        )

        save_design_layout()

        print(
            "Design element uploaded: "
            f"{save_path}"
        )

        return jsonify({

            "success": True,

            "message":
                "Design image uploaded.",

            "element":
                element
        })

    except Exception as error:

        print(
            f"Design upload error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# SERVE DESIGN IMAGE
# ============================================================

@app.route(
    "/design-image/<filename>"
)
def design_image(filename):

    safe_name = Path(
        filename
    ).name

    image_path = (
        DESIGN_FOLDER
        / safe_name
    )

    if not image_path.exists():

        return "", 404

    extension = (
        image_path.suffix.lower()
    )

    if extension == ".png":

        mimetype = (
            "image/png"
        )

    else:

        mimetype = (
            "image/jpeg"
        )

    return send_file(
        image_path,
        mimetype=mimetype
    )


# ============================================================
# DELETE DESIGN IMAGE
# ============================================================

@app.route(
    "/delete-design/<element_id>",
    methods=["POST"]
)
def delete_design(element_id):

    try:

        element = next(
            (
                item
                for item
                in design_config.DESIGN_ELEMENTS
                if item.get("id")
                == element_id
            ),
            None
        )

        if element is None:

            return jsonify({

                "success": False,

                "message":
                    "Design element not found."

            }), 404

        filename = Path(
            str(
                element.get(
                    "filename",
                    ""
                )
            )
        ).name

        design_config.DESIGN_ELEMENTS.remove(
            element
        )

        save_design_layout()

        if filename:

            image_path = (
                DESIGN_FOLDER
                / filename
            )

            if image_path.exists():

                image_path.unlink()

        return jsonify({

            "success": True,

            "message":
                "Design element deleted."
        })

    except Exception as error:

        print(
            f"Delete design error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# SAVE DESIGN ELEMENTS
# ============================================================

@app.route(
    "/save-design-elements",
    methods=["POST"]
)
def save_design_elements():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        elements = data.get(
            "design_elements"
        )

        if not isinstance(
            elements,
            list
        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid design element data."

            }), 400

        existing_files = {

            item.get("id"):
                Path(
                    str(
                        item.get(
                            "filename",
                            ""
                        )
                    )
                ).name

            for item
            in design_config.DESIGN_ELEMENTS
        }

        cleaned = []

        for index, element in enumerate(
            elements
        ):

            element_id = str(
                element.get(
                    "id",
                    ""
                )
            ).strip()

            if not element_id:
                continue

            filename = (
                existing_files.get(
                    element_id
                )
            )

            if not filename:
                continue

            x = float(
                element.get(
                    "x",
                    0
                )
            )

            y = float(
                element.get(
                    "y",
                    0
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

            rotation = float(
                element.get(
                    "rotation",
                    0
                )
            )

            width = max(
                0.02,
                min(
                    1.0,
                    width
                )
            )

            height = max(
                0.02,
                min(
                    1.0,
                    height
                )
            )

            x = max(
                0.0,
                min(
                    1.0 - width,
                    x
                )
            )

            y = max(
                0.0,
                min(
                    1.0 - height,
                    y
                )
            )

            original_name = str(
                element.get(
                    "original_name",
                    filename
                )
            )

            cleaned.append({

                "id":
                    element_id,

                "filename":
                    filename,

                "original_name":
                    original_name,

                "x":
                    x,

                "y":
                    y,

                "width":
                    width,

                "height":
                    height,

                "rotation":
                    rotation % 360,

                "z_index":
                    index
            })

        design_config.DESIGN_ELEMENTS = (
            cleaned
        )

        save_design_layout()

        return jsonify({

            "success": True,

            "message":
                "Design elements saved."
        })

    except Exception as error:

        print(
            "Design element save error: "
            f"{error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# SAVE DESIGN SETTINGS
# ============================================================

@app.route(
    "/save-design",
    methods=["POST"]
)
def save_design():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No design data received."

            }), 400

        # ----------------------------------------------------
        # EVENT TEXT
        # ----------------------------------------------------

        if "event_name" in data:

            design_config.EVENT_NAME = str(
                data["event_name"]
            )

        if "event_subtitle" in data:

            design_config.EVENT_SUBTITLE = str(
                data["event_subtitle"]
            )

        if "bottom_text" in data:

            design_config.BOTTOM_TEXT = str(
                data["bottom_text"]
            )

        # ----------------------------------------------------
        # COLORS
        # ----------------------------------------------------

        if "background_color" in data:

            design_config.GRAPHIC_BACKGROUND = (
                hex_to_rgb(
                    data[
                        "background_color"
                    ]
                )
            )

        if "event_text_color" in data:

            design_config.EVENT_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "event_text_color"
                    ]
                )
            )

        if "subtitle_text_color" in data:

            design_config.SUBTITLE_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "subtitle_text_color"
                    ]
                )
            )

        if "bottom_text_color" in data:

            design_config.BOTTOM_TEXT_COLOR = (
                hex_to_rgb(
                    data[
                        "bottom_text_color"
                    ]
                )
            )

        # ----------------------------------------------------
        # FONT SIZES
        # ----------------------------------------------------

        if "event_font_size" in data:

            design_config.EVENT_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "event_font_size"
                    ]
                )
            )

        if "subtitle_font_size" in data:

            design_config.SUBTITLE_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "subtitle_font_size"
                    ]
                )
            )

        if "bottom_font_size" in data:

            design_config.BOTTOM_FONT_SIZE_PERCENT = (
                float(
                    data[
                        "bottom_font_size"
                    ]
                )
            )

        # ----------------------------------------------------
        # BACKGROUND STYLE
        # ----------------------------------------------------

        if "collage_background_style" in data:

            style = str(
                data[
                    "collage_background_style"
                ]
            ).lower()

            if style not in (
                "solid",
                "gradient",
                "image"
            ):

                raise ValueError(
                    "Invalid collage "
                    "background style."
                )

            design_config.COLLAGE_BACKGROUND_STYLE = (
                style
            )

        # ----------------------------------------------------
        # SOLID BACKGROUND
        # ----------------------------------------------------

        if "collage_background_color" in data:

            design_config.COLLAGE_BACKGROUND_COLOR = (
                hex_to_rgb(
                    data[
                        "collage_background_color"
                    ]
                )
            )

        # ----------------------------------------------------
        # GRADIENT
        # ----------------------------------------------------

        if "collage_gradient_start" in data:

            design_config.COLLAGE_GRADIENT_START = (
                hex_to_rgb(
                    data[
                        "collage_gradient_start"
                    ]
                )
            )

        if "collage_gradient_end" in data:

            design_config.COLLAGE_GRADIENT_END = (
                hex_to_rgb(
                    data[
                        "collage_gradient_end"
                    ]
                )
            )

        if "collage_gradient_direction" in data:

            direction = str(
                data[
                    "collage_gradient_direction"
                ]
            ).lower()

            if direction not in (
                "horizontal",
                "vertical",
                "diagonal"
            ):

                raise ValueError(
                    "Invalid gradient direction."
                )

            design_config.COLLAGE_GRADIENT_DIRECTION = (
                direction
            )

        # ----------------------------------------------------
        # PERSIST SETTINGS
        # ----------------------------------------------------

        DESIGN_SETTINGS_FILE.write_text(
            json.dumps(
                data,
                indent=4
            ),
            encoding="utf-8"
        )

        return jsonify({

            "success": True,

            "message":
                "Design settings saved."
        })

    except Exception as error:

        print(
            f"Design save error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# CAMERA - CONNECT
# ============================================================

@app.route(
    "/connect",
    methods=["POST"]
)
def connect_camera():

    try:

        camera.connect()

        camera.start_liveview()

        return jsonify({

            "success": True,

            "message":
                "Camera connected successfully."
        })

    except Exception as error:

        print(
            f"Camera connection error: "
            f"{error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# CAMERA - DISCONNECT
# ============================================================

@app.route(
    "/disconnect",
    methods=["POST"]
)
def disconnect_camera():

    try:

        camera.disconnect()

        return jsonify({

            "success": True,

            "message":
                "Camera disconnected."
        })

    except Exception as error:

        print(
            f"Camera disconnect error: "
            f"{error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# LIVE VIEW
# ============================================================

@app.route("/liveview")
def liveview():

    def generate():

        while True:

            frame = (
                camera.get_liveview_frame()
            )

            if frame is not None:

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(
                        len(frame)
                    ).encode()
                    + b"\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

            else:

                time.sleep(
                    0.05
                )

    return Response(
        generate(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )


# ============================================================
# START PHOTO SESSION
# ============================================================

@app.route(
    "/start-session",
    methods=["POST"]
)
def start_session():

    global session_active
    global session_photos
    global latest_cloud_session

    # Start collecting the exact camera files
    # belonging to this session.

    session_active = True

    session_photos = []

    # Clear previous digital-gallery information.

    latest_cloud_session = None

    return jsonify({

        "success": True,

        "message":
            "Session started."
    })


# ============================================================
# TAKE PHOTO
# ============================================================

@app.route(
    "/take-photo",
    methods=["POST"]
)
def take_photo():

    global session_photos

    try:

        filepath = (
            camera.take_picture()
        )

        if session_active:

            session_photos.append(
                filepath
            )

        print(
            "Photo added to session: "
            f"{filepath}"
        )

        print(
            "Session photo count: "
            f"{len(session_photos)}"
        )

        return jsonify({

            "success": True,

            "message":
                "Photo taken successfully.",

            "filename":
                filepath.name,

            "photo_number":
                len(session_photos)
        })

    except Exception as error:

        print(
            f"Photo error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# CREATE COLLAGE + DIGITAL GALLERY
# ============================================================

@app.route(
    "/make-collage",
    methods=["POST"]
)
def make_collage_route():

    global latest_collage
    global latest_cloud_session
    global session_active

    # --------------------------------------------------------
    # REQUIRE EXACTLY THREE SESSION PHOTOS
    # --------------------------------------------------------

    if len(session_photos) != 3:

        return jsonify({

            "success": False,

            "message":
                "Need exactly 3 photos."

        }), 400

    try:

        # ----------------------------------------------------
        # CREATE LOCAL COLLAGE
        # ----------------------------------------------------

        collage_path = (
            make_collage(
                session_photos
            )
        )

        latest_collage = Path(
            collage_path
        )

        session_active = False

        print()
        print(
            "=========================================="
        )

        print(
            "LOCAL COLLAGE CREATED"
        )

        print(
            "=========================================="
        )

        print(
            latest_collage
        )

        # ----------------------------------------------------
        # CLOUD UPLOAD
        #
        # Cloud failure intentionally does NOT make
        # collage creation fail.
        #
        # Guests can still preview and print locally.
        # ----------------------------------------------------

        latest_cloud_session = None

        cloud_error = None

        try:

            print()
            print(
                "Uploading PhotoBean session "
                "to cloud..."
            )

            # IMPORTANT:
            #
            # We use session_photos directly.
            #
            # We do NOT search C:\Photobooth\Photos
            # for recent files.
            #
            # This guarantees Photo 1/2/3 are the
            # exact files captured in this session.

            latest_cloud_session = (
                upload_session(
                    photo_paths=list(
                        session_photos
                    ),
                    collage_path=(
                        latest_collage
                    )
                )
            )

            print()
            print(
                "PhotoBean digital gallery ready:"
            )

            print(
                latest_cloud_session[
                    "gallery_url"
                ]
            )

        except Exception as error:

            cloud_error = str(
                error
            )

            print()
            print(
                "=========================================="
            )

            print(
                "CLOUD GALLERY WARNING"
            )

            print(
                "=========================================="
            )

            print(
                "The collage was created "
                "successfully."
            )

            print(
                "The digital gallery could "
                "not be uploaded."
            )

            print(
                cloud_error
            )

            print(
                "Local preview and printing "
                "will continue normally."
            )

        # ----------------------------------------------------
        # RESPONSE TO MAIN.JS
        # ----------------------------------------------------

        response_data = {

            "success":
                True,

            "path":
                str(
                    latest_collage
                ),

            "cloud_available":
                (
                    latest_cloud_session
                    is not None
                )
        }

        # ----------------------------------------------------
        # CLOUD SUCCESS
        # ----------------------------------------------------

        if latest_cloud_session:

            response_data[
                "session_id"
            ] = (
                latest_cloud_session[
                    "session_id"
                ]
            )

            response_data[
                "gallery_url"
            ] = (
                latest_cloud_session[
                    "gallery_url"
                ]
            )

        # ----------------------------------------------------
        # CLOUD FAILURE
        # ----------------------------------------------------

        elif cloud_error:

            response_data[
                "cloud_error"
            ] = (
                cloud_error
            )

        return jsonify(
            response_data
        )

    except Exception as error:

        session_active = False

        print()
        print(
            f"Collage error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# DIGITAL GALLERY STATUS
# ============================================================

@app.route("/gallery-status")
def gallery_status():

    if latest_cloud_session is None:

        return jsonify({

            "available":
                False,

            "gallery_url":
                None,

            "session_id":
                None
        })

    return jsonify({

        "available":
            True,

        "gallery_url":
            latest_cloud_session[
                "gallery_url"
            ],

        "session_id":
            latest_cloud_session[
                "session_id"
            ]
    })


# ============================================================
# COLLAGE STATUS
# ============================================================

@app.route("/collage-status")
def collage_status():

    ready = (

        latest_collage is not None

        and latest_collage.exists()
    )

    return jsonify({

        "ready":
            ready,

        "cloud_available":
            (
                latest_cloud_session
                is not None
            )
    })


# ============================================================
# COLLAGE IMAGE
# ============================================================

@app.route("/collage-image")
def collage_image():

    if latest_collage is None:

        return "", 404

    if not latest_collage.exists():

        return "", 404

    return send_file(
        latest_collage,
        mimetype="image/jpeg"
    )


# ============================================================
# PREVIEW LAST COLLAGE
# ============================================================

@app.route(
    "/preview-last-collage"
)
def preview_last_collage():

    if latest_collage is None:

        return jsonify({

            "success": False,

            "message":
                "No collage has been "
                "created yet."

        }), 404

    if not latest_collage.exists():

        return jsonify({

            "success": False,

            "message":
                "The last collage file "
                "no longer exists."

        }), 404

    response_data = {

        "success":
            True,

        "filename":
            latest_collage.name,

        "cloud_available":
            (
                latest_cloud_session
                is not None
            )
    }

    if latest_cloud_session:

        response_data[
            "gallery_url"
        ] = (
            latest_cloud_session[
                "gallery_url"
            ]
        )

        response_data[
            "session_id"
        ] = (
            latest_cloud_session[
                "session_id"
            ]
        )

    return jsonify(
        response_data
    )


# ============================================================
# PRINT COLLAGE
# ============================================================

@app.route(
    "/print-collage",
    methods=["POST"]
)
def print_collage():

    if latest_collage is None:

        return jsonify({

            "success": False,

            "message":
                "There is no collage "
                "to print."

        }), 400

    if not latest_collage.exists():

        return jsonify({

            "success": False,

            "message":
                "The collage file could "
                "not be found."

        }), 404

    try:

        print(
            "Sending collage to printer: "
            f"{latest_collage}"
        )

        print_file(
            latest_collage
        )

        return jsonify({

            "success": True,

            "message":
                "Print job sent successfully."
        })

    except Exception as error:

        print(
            f"Printing error: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        "          PHOTOBOOTH WEB SERVER"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Main Photobooth:"
    )

    print(
        "http://localhost:5000"
    )

    print()

    print(
        "Design Studio:"
    )

    print(
        "http://localhost:5000/design"
    )

    print()

    print(
        "Cloud Gallery:"
    )

    print(
        "https://photobean-gallery."
        "stillmotionarch.workers.dev"
    )

    print()

    print(
        "=========================================="
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )