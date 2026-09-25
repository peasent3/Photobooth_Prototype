# --------------------------------------------------------------
# printer.py
# --------------------------------------------------------------
# Small helper that sends a file (normally the 4×6" collage JPEG)
# to the default operating‑system printer.
#
#   • Windows  → uses the built‑in `mspaint /pt` command
#   • macOS   → uses `lp` (CUPS)
#   • Linux   → also uses `lp` (CUPS)
#
# The function raises an exception if the command fails, so
# your Flask route can return a proper error response.
# --------------------------------------------------------------

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Union

log = logging.getLogger(__name__)

def _run_cmd(cmd: list[str]) -> None:
    """
    Executes *cmd* (a list of command‑line arguments) and raises
    a RuntimeError if the process exits with a non‑zero return code.
    """
    log.debug("Running command: %s", " ".join(cmd))
    try:
        # `check=True` makes subprocess raise CalledProcessError on failure
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        # Attach both stdout & stderr to the exception message – useful for debugging
        stdout = exc.stdout.decode(errors="replace")
        stderr = exc.stderr.decode(errors="replace")
        raise RuntimeError(
            f"Print command failed (exit {exc.returncode}).\n"
            f"STDOUT: {stdout}\nSTDERR: {stderr}"
        ) from exc


def print_file(file_path: Union[str, Path]) -> None:
    """
    Send *file_path* to the default printer.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to the image/PDF you want to print.  The function checks that the
        file exists before attempting to print.

    Raises
    ------
    FileNotFoundError
        If *file_path* does not exist.
    RuntimeError
        If the underlying print command fails.
    NotImplementedError
        If the operating system is not Windows, macOS, or Linux.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    system = platform.system()
    log.info("Printing %s on %s", path, system)

    if system == "Windows":
        # ----------------------------------------------------------
        # Windows printing via the built‑in Microsoft Paint.
        # The `/pt` switch prints the file *without* opening the UI.
        # ----------------------------------------------------------
        # NOTE: `mspaint` must be on the system PATH (it is on all
        # standard Windows installations).  If you have a different
        # printer driver you can replace the command with something
        # like `"powershell", "Start-Process", "-FilePath", str(path), "-Verb", "Print"`.
        # ----------------------------------------------------------
        cmd = ["mspaint", "/pt", str(path)]
        _run_cmd(cmd)

    elif system in ("Linux", "Darwin"):   # macOS reports "Darwin"
        # ----------------------------------------------------------
        # Linux/macOS printing via CUPS (`lp` command).
        # `lp` will use the system's default printer.
        # ----------------------------------------------------------
        cmd = ["lp", str(path)]
        _run_cmd(cmd)

    else:
        raise NotImplementedError(f"Printing not implemented for OS: {system}")

    log.info("Print job submitted successfully.")