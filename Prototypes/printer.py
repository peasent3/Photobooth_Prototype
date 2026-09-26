import os
import win32print
import win32ui
import win32con
from PIL import Image, ImageWin


# ============================================================
# PRINTER SETTINGS
# ============================================================

PRINTER_NAME = "Canon SELPHY CP1500"


# ============================================================
# PRINT POSITION ADJUSTMENT
# ============================================================
#
# Positive X = move image RIGHT
# Negative X = move image LEFT
#
# Positive Y = move image DOWN
# Negative Y = move image UP
#
# Start with these values and adjust if necessary.
#

PRINT_OFFSET_X = 0
PRINT_OFFSET_Y = 0


# ============================================================
# LIST PRINTERS
# ============================================================

def list_printers():
    printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL |
        win32print.PRINTER_ENUM_CONNECTIONS
    )

    print("Installed printers:")

    for printer in printers:
        print(f"  - {printer[2]}")

    print()


# ============================================================
# CHECK PRINTER
# ============================================================

def printer_exists():
    printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL |
        win32print.PRINTER_ENUM_CONNECTIONS
    )

    printer_names = [printer[2] for printer in printers]

    return PRINTER_NAME in printer_names


# ============================================================
# PRINT IMAGE
# ============================================================

def print_file(image_path):

    image_path = os.path.abspath(str(image_path))

    print()
    print("===================================")
    print("         PRINTING PHOTO")
    print("===================================")
    print()

    print(f"Printer: {PRINTER_NAME}")
    print(f"Image:   {image_path}")

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image file does not exist: {image_path}"
        )

    # --------------------------------------------------------
    # Check printer
    # --------------------------------------------------------

    if not printer_exists():
        raise RuntimeError(
            f"Printer '{PRINTER_NAME}' was not found."
        )

    # --------------------------------------------------------
    # Open image
    # --------------------------------------------------------

    image = Image.open(image_path)

    print(f"Image size: {image.size}")
    print(f"Image DPI:  {image.info.get('dpi')}")

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    # --------------------------------------------------------
    # Open printer
    # --------------------------------------------------------

    printer_handle = win32print.OpenPrinter(PRINTER_NAME)

    try:

        # ----------------------------------------------------
        # Get printer DEVMODE
        # ----------------------------------------------------

        printer_info = win32print.GetPrinter(
            printer_handle,
            2
        )

        devmode = printer_info["pDevMode"]

        # ----------------------------------------------------
        # FORCE LANDSCAPE
        # ----------------------------------------------------

        devmode.Orientation = 2
        devmode.Fields |= win32con.DM_ORIENTATION

        # ----------------------------------------------------
        # Create printer DC
        # ----------------------------------------------------

        dc = win32ui.CreateDC()

        dc.CreatePrinterDC(PRINTER_NAME)

        # ----------------------------------------------------
        # Get printer dimensions
        # ----------------------------------------------------

        printable_width = dc.GetDeviceCaps(
            win32con.HORZRES
        )

        printable_height = dc.GetDeviceCaps(
            win32con.VERTRES
        )

        physical_width = dc.GetDeviceCaps(
            win32con.PHYSICALWIDTH
        )

        physical_height = dc.GetDeviceCaps(
            win32con.PHYSICALHEIGHT
        )

        offset_x = dc.GetDeviceCaps(
            win32con.PHYSICALOFFSETX
        )

        offset_y = dc.GetDeviceCaps(
            win32con.PHYSICALOFFSETY
        )

        print()
        print("Printer dimensions:")
        print(
            f"  Printable area: "
            f"{printable_width} x {printable_height}"
        )

        print(
            f"  Physical size: "
            f"{physical_width} x {physical_height}"
        )

        print(
            f"  Printer offset: "
            f"{offset_x} x {offset_y}"
        )

        # ----------------------------------------------------
        # Determine orientation
        # ----------------------------------------------------

        if printable_width < printable_height:

            print("Printer reports PORTRAIT.")
            print("Rotating image 90 degrees.")

            image_to_print = image.rotate(
                90,
                expand=True
            )

        else:

            print("Printer reports LANDSCAPE.")

            image_to_print = image

        # ----------------------------------------------------
        # Image dimensions
        # ----------------------------------------------------

        image_width, image_height = image_to_print.size

        # ----------------------------------------------------
        # Scale image to fit printable area
        # ----------------------------------------------------

        scale_x = printable_width / image_width
        scale_y = printable_height / image_height

        scale = min(scale_x, scale_y)

        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # ----------------------------------------------------
        # Center image
        # ----------------------------------------------------

        x = (
            printable_width - new_width
        ) // 2

        y = (
            printable_height - new_height
        ) // 2

        # ----------------------------------------------------
        # MANUAL POSITION ADJUSTMENT
        # ----------------------------------------------------

        x += PRINT_OFFSET_X
        y += PRINT_OFFSET_Y

        # ----------------------------------------------------
        # Display final position
        # ----------------------------------------------------

        print()
        print("Final print position:")
        print(f"  X:      {x}")
        print(f"  Y:      {y}")
        print(f"  Width:  {new_width}")
        print(f"  Height: {new_height}")

        print()
        print(
            f"Manual adjustment: "
            f"X={PRINT_OFFSET_X}, "
            f"Y={PRINT_OFFSET_Y}"
        )

        # ----------------------------------------------------
        # Start print
        # ----------------------------------------------------

        dc.StartDoc(
            os.path.basename(image_path)
        )

        dc.StartPage()

        # ----------------------------------------------------
        # Draw image
        # ----------------------------------------------------

        dib = ImageWin.Dib(image_to_print)

        dib.draw(
            dc.GetHandleOutput(),
            (
                x,
                y,
                x + new_width,
                y + new_height
            )
        )

        # ----------------------------------------------------
        # Finish
        # ----------------------------------------------------

        dc.EndPage()
        dc.EndDoc()

        print()
        print("Print job sent successfully.")
        print()

        dc.DeleteDC()

    finally:

        win32print.ClosePrinter(printer_handle)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print("      CANON SELPHY CP1500")
    print("          PRINTER TEST")
    print("===================================")
    print()

    list_printers()

    if printer_exists():

        print(f"Printer found: {PRINTER_NAME}")
        print()

        test_image = (
            r"C:\Photobooth\Photos\photobooth_collage.jpg"
        )

        if os.path.exists(test_image):

            print_file(test_image)

        else:

            print("Test image not found:")
            print(test_image)

    else:

        print(f"Printer NOT found: {PRINTER_NAME}")