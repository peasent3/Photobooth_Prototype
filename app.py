# --------------------------------------------------------------
# app.py
# --------------------------------------------------------------
# Flask controller – very small UI (no custom JS / CSS)
# --------------------------------------------------------------

import logging
from pathlib import Path

from flask import Flask, jsonify, Response, render_template, redirect, url_for

# ----------------------------------------------------------------------
# Local imports (your existing modules)
# ----------------------------------------------------------------------
from camera import A7CII                # wrapper that already has a collage callback
from collage import make_collage        # builds the 4×6 collage
from printer import print_file          # optional printing stub

# ----------------------------------------------------------------------
# Flask app & logger
# ----------------------------------------------------------------------
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("photobooth")

# ----------------------------------------------------------------------
# Collage callback (unchanged – you can keep it exactly as you already have)
# ----------------------------------------------------------------------
def _collage_ready(paths):
    try:
        collage_path = make_collage(paths)
        app.config["LATEST_COLLAGE"] = collage_path
        log.info("Collage created → %s", collage_path)
    except Exception as exc:                       # pragma: no cover
        log.exception("Failed to create collage: %s", exc)

# ----------------------------------------------------------------------
# One global camera instance
# ----------------------------------------------------------------------
camera = A7CII(collage_callback=_collage_ready)

# --------------------------------------------------------------
# HOME PAGE – show live view and connect/disconnect buttons
# --------------------------------------------------------------
@app.route("/")
def index():
    """
    Render the UI.  The template receives a ``connected`` boolean that is
    True when the camera object is already instantiated.
    """
    connected = camera.camera is not None
    return render_template("index.html", connected=connected)

# --------------------------------------------------------------
# CONNECT
# --------------------------------------------------------------
@app.route("/connect", methods=["POST"])
def connect_camera():
    try:
        camera.connect()
        camera.start_liveview()
        log.info("Camera connected")
    except Exception as exc:
        log.exception("Connect error")
        # Even on error we still go back to the home page – the toast will
        # display the message (see the optional toast section at the bottom).
        return jsonify(success=False, message=str(exc)), 500

    # Redirect so the page reloads and the “connected” flag updates
    return redirect(url_for("index"))

# --------------------------------------------------------------
# DISCONNECT
# --------------------------------------------------------------
@app.route("/disconnect", methods=["POST"])
def disconnect_camera():
    try:
        camera.disconnect()
        log.info("Camera disconnected")
    except Exception as exc:
        log.exception("Disconnect error")
        return jsonify(success=False, message=str(exc)), 500

    return redirect(url_for("index"))

# --------------------------------------------------------------
# LIVE VIEW (MJPEG stream)
# --------------------------------------------------------------
@app.route("/liveview")
def liveview():
    """
    Streams JPEG frames from the camera as a multipart response.
    The <img> tag in the template points to this endpoint.
    """
    def generate():
        while True:
            frame = camera.get_liveview_frame()
            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
                    + frame + b"\r\n"
                )
            else:
                # No frame yet – pause a little so we don’t spin the CPU.
                import time
                time.sleep(0.05)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

# --------------------------------------------------------------
# PRINT COLLAGE (optional – keep if you want printing)
# --------------------------------------------------------------
@app.route("/print-collage", methods=["POST"])
def print_collage():
    collage_path: Path = app.config.get("LATEST_COLLAGE")   # type: ignore[assignment]
    if not collage_path or not collage_path.exists():
        return jsonify(success=False, message="No collage available yet."), 404

    try:
        print_file(collage_path)
        return jsonify(success=True, message="Collage sent to printer.")
    except Exception as exc:          # pragma: no cover
        log.exception("Print error")
        return jsonify(success=False, message=str(exc)), 500

# --------------------------------------------------------------
# ENTRY POINT
# --------------------------------------------------------------
if __name__ == "__main__":
    log.info("Starting Photobooth web server …")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)