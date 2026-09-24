from pathlib import Path
import time

PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")

PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)

print("===================================")
print("       PHOTOBOOTH CAMERA TEST")
print("===================================")
print()
print("Waiting for a new photograph...")
print()

existing_files = set(PHOTO_FOLDER.glob("*"))

while True:

    current_files = set(PHOTO_FOLDER.glob("*"))

    new_files = current_files - existing_files

    if new_files:

        for photo in new_files:

            if photo.suffix.lower() in [".jpg", ".jpeg"]:

                print("📸 NEW PHOTO!")
                print(f"File: {photo}")
                print(f"Size: {photo.stat().st_size:,} bytes")
                print()

        existing_files = current_files

    time.sleep(0.5)
