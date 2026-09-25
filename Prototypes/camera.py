from pathlib import Path
from datetime import datetime
import threading

from pysonycam import SonyCamera


PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")


class A7CII:
    def __init__(self, save_folder=PHOTO_FOLDER):
        self.save_folder = Path(save_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)

        self.camera = None

        # Live View
        self.liveview_running = False
        self.liveview_thread = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()

    def connect(self):
        print("Connecting to Sony camera...")

        self.camera = SonyCamera()

        print("Opening USB/PTP connection...")
        self.camera.connect()

        print("Authenticating with Sony camera...")
        self.camera.authenticate()

        self.camera.set_mode("still")

        print("Camera connected.")

    def take_picture(self):
        if self.camera is None:
            raise RuntimeError("Camera is not connected.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = self.save_folder / filename

        print("Taking picture...")

        self.camera.capture(str(filepath))

        print(f"Photo saved: {filepath}")

        return filepath

    # ---------------------------------------------------------
    # LIVE VIEW
    # ---------------------------------------------------------

    def start_liveview(self):
        if self.camera is None:
            raise RuntimeError("Camera is not connected.")

        if self.liveview_running:
            return

        print("Starting Live View...")

        self.liveview_running = True

        self.liveview_thread = threading.Thread(
            target=self._liveview_loop,
            daemon=True
        )

        self.liveview_thread.start()

    def _liveview_loop(self):
        try:
            for frame in self.camera.liveview_stream(
                count=0,
                interval=0.05
            ):
                if not self.liveview_running:
                    break

                with self.frame_lock:
                    self.latest_frame = frame

        except Exception as error:
            print(f"Live View error: {error}")

        finally:
            self.liveview_running = False

    def get_liveview_frame(self):
        with self.frame_lock:
            return self.latest_frame

    def stop_liveview(self):
        if not self.liveview_running:
            return

        print("Stopping Live View...")

        self.liveview_running = False

        if self.liveview_thread is not None:
            self.liveview_thread.join(timeout=2)

        self.liveview_thread = None

        with self.frame_lock:
            self.latest_frame = None

    # ---------------------------------------------------------
    # DISCONNECT
    # ---------------------------------------------------------

    def disconnect(self):
        print("Disconnecting camera...")

        # Stop Live View first
        self.stop_liveview()

        if self.camera is not None:
            try:
                self.camera.disconnect()
            except Exception:
                pass

            self.camera = None

        print("Camera disconnected.")