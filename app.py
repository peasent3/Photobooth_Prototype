from flask import Flask, render_template, jsonify, Response
from camera import A7CII
import time


app = Flask(__name__)

camera = A7CII()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/connect", methods=["POST"])
def connect_camera():
    try:
        camera.connect()

        # Start Live View after successful connection
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


@app.route("/take-photo", methods=["POST"])
def take_photo():
    try:
        filepath = camera.take_picture()

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


if __name__ == "__main__":
    print("Starting Photobooth Web Server...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )