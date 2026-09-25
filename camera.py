# --------------------------------------------------------------
# camera.py
# --------------------------------------------------------------
# Sony A7C II wrapper
#   • Fixed constructor (__init__) – now accepts a collage callback
#   • Guarantees a stable JPEG file before it is used
#   • Provides live‑view in a background thread
# --------------------------------------------------------------

import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from pysonycam import SonyCamera

# ----------------------------------------------------------------------
# Default folder – you can change it here or pass a different path
# ----------------------------------------------------------------------
DEFAULT_PHOTO_FOLDER = Path(r"C:\Photobooth\Photos")
DEFAULT_PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)


class A7CII:
    """
    Minimal, thread‑safe wrapper around ``pysonycam.SonyCamera``.
    """

    def __init__(
        self,
        save_folder: Path = DEFAULT_PHOTO_FOLDER,
        collage_callback: Optional[Callable[[List[Path]], None]] = None,
    ) -> None:
        # ---- folders ----------------------------------------------------
        self.save_folder: Path = Path(save_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)

        # ---- Sony camera ------------------------------------------------
        self.camera: Optional[SonyCamera] = None

        # ---- live‑view state -------------------------------------------
        self.liveview_running = False
        self.liveview_thread: Optional[threading.Thread] = None
        self._latest_frame: Optional[bytes] = None
        self._frame_lock = threading.Lock()

        # ---- collage bookkeeping ----------------------------------------
        self._pic_counter = 0
        self._collage_cb = collage_callback      # ← store the callback

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------
    def connect(self) -> None:
        if self.camera is not None:
            raise RuntimeError("Camera already connected.")
        print("[CAM] Connecting …")
        self.camera = SonyCamera()
        self.camera.connect()
        self.camera.authenticate()
        self.camera.set_mode("still")
        print("[CAM] Connected.")

    # ------------------------------------------------------------------
    # LIVE‑VIEW
    # ------------------------------------------------------------------
    def start_liveview(self) -> None:
        if self.camera is None:
            raise RuntimeError("Camera not connected.")
        if self.liveview_running:
            return
        print("[CAM] Starting live view …")
        self.liveview_running = True
        self.liveview_thread = threading.Thread(
            target=self._liveview_loop, daemon=True
        )
        self.liveview_thread.start()

    def _liveview_loop(self) -> None:
        try:
            for frame in self.camera.liveview_stream(count=0, interval=0.05):
                if not self.liveview_running:
                    break
                with self._frame_lock:
                    self._latest_frame = frame
        except Exception as err:  # defensive – should never crash the app
            print(f"[CAM] Live view error: {err}")
        finally:
            self.liveview_running = False
            self.liveview_thread = None
            print("[CAM] Live view stopped.")

    def get_liveview_frame(self) -> Optional[bytes]:
        with self._frame_lock:
            return self._latest_frame

    def stop_liveview(self) -> None:
        if not self.liveview_running:
            return
        print("[CAM] Stopping live view …")
        self.liveview_running = False
        if self.liveview_thread is not None:
            self.liveview_thread.join(timeout=2)
        self.liveview_thread = None
        with self._frame_lock:
            self._latest_frame = None

    # ------------------------------------------------------------------
    # HELPER – wait until a file stops growing
    # ------------------------------------------------------------------
    @staticmethod
    def _wait_until_stable(
        path: Path, timeout: float = 5.0, poll: float = 0.3
    ) -> None:
        """
        Cameras sometimes write a file in chunks.  This blocks until the
        size stays the same for one poll interval (or the timeout expires).
        """
        last = -1
        elapsed = 0.0
        while elapsed < timeout:
            try:
                cur = path.stat().st_size
            except FileNotFoundError:
                return
            if cur == last:
                return
            last = cur
            time.sleep(poll)
            elapsed += poll

    # ------------------------------------------------------------------
    # TAKE A PICTURE
    # ------------------------------------------------------------------
    def take_picture(self) -> Path:
        if self.camera is None:
            raise RuntimeError("Camera not connected.")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{ts}.jpg"
        dest = self.save_folder / filename

        print("[CAM] Capturing …")
        self.camera.capture(str(dest))
        self._wait_until_stable(dest)          # ensure the file is complete
        print(f"[CAM] Saved → {dest}")

        # ---- collage bookkeeping ---------------------------------------
        self._pic_counter += 1
        if self._pic_counter >= 4 and callable(self._collage_cb):
            # Get the four most recent JPEGs (by creation time)
            recent = sorted(
                self.save_folder.glob("*.jpg"),
                key=lambda p: p.stat().st_ctime,
                reverse=True,
            )[:4]
            print("[CAM] 4 pictures collected – calling collage callback.")
            self._collage_cb(list(recent))
            self._pic_counter = 0   # reset for the next batch

        return dest

    # ------------------------------------------------------------------
    # DISCONNECT
    # ------------------------------------------------------------------
    def disconnect(self) -> None:
        print("[CAM] Disconnecting …")
        self.stop_liveview()
        if self.camera is not None:
            try:
                self.camera.disconnect()
            except Exception:
                pass
            self.camera = None
        print("[CAM] Disconnected.")
        