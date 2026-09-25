from pathlib import Path
from datetime import datetime
import msvcrt
import time

from pysonycam import SonyCamera



PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")


class A7CII:
    """Control a Sony A7C II connected to the PC via USB."""

    def __init__(self, save_folder=PHOTO_FOLDER):
        self.save_folder = Path(save_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)

        self.camera = None

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
        """Take a picture and save the JPEG to the PC."""

        if self.camera is None:
            raise RuntimeError("Camera is not connected.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"photo_{timestamp}.jpg"
        filepath = self.save_folder / filename

        print("Taking picture...")

        self.camera.capture(str(filepath))

        print(f"Photo saved:")
        print(filepath)

        return filepath

    def disconnect(self):
        """Disconnect from the camera."""

        if self.camera is not None:
            self.camera.disconnect()
            self.camera = None

        print("Camera disconnected.")


if __name__ == "__main__":
    camera = A7CII()

    try:
        camera.connect()

        print("\n===================================")
        print("          PHOTOBOOTH READY")
        print("===================================")
        print("Press ENTER to take a photo.")
        print("Press SPACE to exit.")
        print("===================================\n")

        while True:
            print("Ready: ", end="", flush=True)

            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()

                    # SPACE = exit immediately
                    if key == b" ":
                        print("\n\nExiting photobooth...")
                        raise SystemExit

                    # ENTER = take picture
                    elif key == b"\r":
                        print()
                        camera.take_picture()
                        print()
                        break

                time.sleep(0.05)

    except SystemExit:
        pass

    except Exception as error:
        print("\nERROR:")
        print(error)

    finally:
        camera.disconnect()