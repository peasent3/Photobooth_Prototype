from flask import Flask, render_template, jsonify, Response, send_file
import time
from pathlib import Path

from camera import A7CII
from collage import make_collage
from printer import print_file


app = Flask(__name__)

camera = A7CII()

session_active = False
session_photos: list[Path] = []

# Stores the most recently created collage
latest_collage = None


@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# CAMERA
# ============================================================

@app.route("/connect", methods=["POST"])
def connect_camera():
    try:
        camera.connect()
        camera.start_liveview()

        return jsonify({
            "success": True,
            "message": "Camera connected successfully."
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/disconnect", methods=["POST"])
def disconnect_camera():
    try:
        camera.disconnect()

        return jsonify({
            "success": True,
            "message": "Camera disconnected."
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# LIVE VIEW
# ============================================================

@app.route("/liveview")
def liveview():

    def generate():

        while True:

            frame = camera.get_liveview_frame()

            if frame is not None:

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(len(frame)).encode()
                    + b"\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

            else:
                time.sleep(0.05)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================
# PHOTO SESSION
# ============================================================

@app.route("/start-session", methods=["POST"])
def start_session():

    global session_active
    global session_photos

    session_active = True
    session_photos = []

    return jsonify({
        "success": True,
        "message": "Session started."
    })


@app.route("/take-photo", methods=["POST"])
def take_photo():

    global session_photos

    try:

        filepath = camera.take_picture()

        if session_active:
            session_photos.append(filepath)

        return jsonify({
            "success": True,
            "message": "Photo taken successfully.",
            "filename": filepath.name
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# COLLAGE
# ============================================================

@app.route("/make-collage", methods=["POST"])
def make_collage_route():

    global session_active
    global session_photos
    global latest_collage

    if not session_active:

        return jsonify({
            "success": False,
            "message": "No active session."
        }), 400

    if len(session_photos) != 4:

        return jsonify({
            "success": False,
            "message": (
                f"Need exactly 4 photos, "
                f"have {len(session_photos)}."
            )
        }), 400

    try:

        print("Creating 4-photo collage...")

        collage_path = make_collage(session_photos)

        latest_collage = Path(collage_path)

        session_active = False
        session_photos = []

        print(f"Collage created: {latest_collage}")

        return jsonify({
            "success": True,
            "message": "Collage created.",
            "collage": latest_collage.name
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# LAST COLLAGE / PREVIEW
# ============================================================

@app.route("/collage-status")
def collage_status():

    ready = (
        latest_collage is not None
        and latest_collage.exists()
    )

    return jsonify({
        "ready": ready
    })


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


# This route is specifically for the
# "Preview Last Collage" button.
@app.route("/preview-last-collage")
def preview_last_collage():

    if latest_collage is None:
        return jsonify({
            "success": False,
            "message": "No collage has been created yet."
        }), 404

    if not latest_collage.exists():
        return jsonify({
            "success": False,
            "message": "The last collage file no longer exists."
        }), 404

    return jsonify({
        "success": True,
        "filename": latest_collage.name
    })


# ============================================================
# PRINT
# ============================================================

@app.route("/print-collage", methods=["POST"])
def print_collage():

    if latest_collage is None:

        return jsonify({
            "success": False,
            "message": "There is no collage to print."
        }), 400

    if not latest_collage.exists():

        return jsonify({
            "success": False,
            "message": "The collage file could not be found."
        }), 404

    try:

        print(f"Sending collage to printer: {latest_collage}")

        print_file(latest_collage)

        return jsonify({
            "success": True,
            "message": "Print job sent successfully."
        })

    except Exception as error:

        print(f"Printing error: {error}")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print("     PHOTOBOOTH WEB SERVER")
    print("===================================")
    print()
    print("Starting server...")
    print("Open http://localhost:5000")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )