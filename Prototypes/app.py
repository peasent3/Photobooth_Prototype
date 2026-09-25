# --------------------------------------------------------------
# app.py  – original UI + new “session” logic
# --------------------------------------------------------------
from flask import Flask, render_template, jsonify, Response, send_file
import time
from pathlib import Path

# ---------- ORIGINAL IMPORT ----------
from camera import A7CII

# ---------- NEW IMPORT ----------
from collage import make_collage               # helper that builds the collage

app = Flask(__name__)

# ------------------------------------------------------------------
# GLOBAL CAMERA INSTANCE (unchanged)
# ------------------------------------------------------------------
camera = A7CII()          # uses the fixed __init__ in camera.py

# ------------------------------------------------------------------
# SESSION STATE – stores the four freshly‑taken pictures
# ------------------------------------------------------------------
session_active = False          # True while a session is running
session_photos: list[Path] = [] # Paths of the four pictures taken in the session


# --------------------------------------------------------------
# HOME PAGE
# --------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------------------
# CONNECT
# --------------------------------------------------------------
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


# --------------------------------------------------------------
# START SESSION  – resets the session list and enables picture capture
# --------------------------------------------------------------
@app.route("/start-session", methods=["POST"])
def start_session():
    """
    Called once when the user presses the **Start Session** button.
    It clears any previous session data and tells the server that the
    next four `/take-photo` calls belong to a new session.
    """
    global session_active, session_photos
    session_active = True
    session_photos = []            # empty list – will be filled by take‑photo
    return jsonify({"success": True, "message": "Session started."})


# --------------------------------------------------------------
# TAKE PHOTO  – unchanged, but now also tracks session pictures
# --------------------------------------------------------------
@app.route("/take-photo", methods=["POST"])
def take_photo():
    """
    Capture a single picture.
    If a session is active, the path of this picture is stored so that
    a collage can later be built from exactly the four pictures taken
    during this session.
    """
    global session_active, session_photos
    try:
        filepath = camera.take_picture()

        # -----------------------------------------------------------------
        # If we are currently inside a “session”, remember the picture.
        # -----------------------------------------------------------------
        if session_active:
            session_photos.append(filepath)
            # When the fourth picture is captured we *do not* build the collage
            # here – the front‑end will explicitly request it via /make-collage.
            # This keeps the UI free to show the 3‑2‑1 countdown.
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


# --------------------------------------------------------------
# MAKE COLLAGE  – builds a collage from the four pictures captured
#                 during the current session.
# --------------------------------------------------------------
@app.route("/make-collage", methods=["POST"])
def make_collage_route():
    """
    After the fourth picture of a session has been taken this endpoint
    creates the 4 × 6″ collage from **exactly those four images**,
    stores the collage path in ``app.config["LATEST_COLLAGE"]`` and
    returns the collage filename.
    """
    global session_active, session_photos

    if not session_active:
        return jsonify({
            "success": False,
            "message": "No active session."
        }), 400

    if len(session_photos) != 4:
        return jsonify({
            "success": False,
            "message": f"Need exactly 4 photos, have {len(session_photos)}."
        }), 400

    try:
        collage_path = make_collage(session_photos)   # <-- collage.py does the work
        # Reset session state – a new session will need a fresh list.
        session_active = False
        session_photos = []

        # Store the collage so other routes (e.g., a Print button) can use it.
        app.config["LATEST_COLLAGE"] = collage_path
        return jsonify({
            "success": True,
            "message": "Collage created.",
            "collage": collage_path.name
        })
    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


# --------------------------------------------------------------
# DISCONNECT
# --------------------------------------------------------------
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


# --------------------------------------------------------------
# LIVE VIEW (MJPEG stream) – unchanged
# --------------------------------------------------------------
@app.route("/liveview")
def liveview():
    """
    Streams JPEG frames from the camera as a multipart MJPEG response.
    The <img> tag in index.html points to this endpoint.
    """
    def generate():
        while True:
            frame = camera.get_liveview_frame()
            if frame is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
                    + frame + b"\r\n"
                )
            else:
                time.sleep(0.05)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------------------
# SERVE THE LAST COLLAGE IMAGE (so the browser can display it)
# --------------------------------------------------------------
@app.route("/collage-image")
def collage_image():
    """
    Returns the most‑recent collage file (generated by /make-collage)
    as a JPEG image.  Used by the front‑end to show the final picture.
    """
    collage_path = app.config.get("LATEST_COLLAGE")
    if not collage_path or not Path(collage_path).exists():
        return "", 404
    return send_file(collage_path, mimetype="image/jpeg")


# --------------------------------------------------------------
# OPTIONAL: expose collage status (useful for a separate Print button)
# --------------------------------------------------------------
@app.route("/collage-status")
def collage_status():
    ready = "LATEST_COLLAGE" in app.config and Path(app.config["LATEST_COLLAGE"]).exists()
    return jsonify(ready=ready)


# --------------------------------------------------------------
# RUN THE SERVER
# --------------------------------------------------------------
if __name__ == "__main__":
    print("Starting Photobooth Web Server...")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)