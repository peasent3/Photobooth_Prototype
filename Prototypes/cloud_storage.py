import os
import secrets
import mimetypes
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


# ============================================================
# PHOTO BEAN CLOUD CONFIGURATION
# ============================================================

R2_ACCESS_KEY = os.getenv(
    "PHOTO_BEAN_R2_ACCESS_KEY"
)

R2_SECRET_KEY = os.getenv(
    "PHOTO_BEAN_R2_SECRET_KEY"
)

R2_ENDPOINT = os.getenv(
    "PHOTO_BEAN_R2_ENDPOINT"
)

R2_BUCKET = os.getenv(
    "PHOTO_BEAN_R2_BUCKET",
    "photobean-sessions"
)


# Public Cloudflare Worker used for guest galleries.
GALLERY_BASE_URL = os.getenv(
    "PHOTO_BEAN_GALLERY_BASE_URL",
    "https://photobean-gallery.stillmotionarch.workers.dev"
).rstrip("/")


# PhotoBean's working photo folder.
PHOTO_FOLDER = Path(
    r"C:\Photobooth\Photos"
)


# ============================================================
# CONFIGURATION CHECK
# ============================================================

def check_configuration():
    """
    Make sure all required Cloudflare R2 environment
    variables are available.
    """

    missing = []

    if not R2_ACCESS_KEY:
        missing.append(
            "PHOTO_BEAN_R2_ACCESS_KEY"
        )

    if not R2_SECRET_KEY:
        missing.append(
            "PHOTO_BEAN_R2_SECRET_KEY"
        )

    if not R2_ENDPOINT:
        missing.append(
            "PHOTO_BEAN_R2_ENDPOINT"
        )

    if not R2_BUCKET:
        missing.append(
            "PHOTO_BEAN_R2_BUCKET"
        )


    if missing:
        raise RuntimeError(
            "Missing environment variables:\n"
            + "\n".join(
                f"- {name}"
                for name in missing
            )
        )


# ============================================================
# R2 CLIENT
# ============================================================

def get_r2_client():
    """
    Create and return the S3-compatible
    Cloudflare R2 client.
    """

    check_configuration()


    return boto3.client(
        service_name="s3",

        endpoint_url=R2_ENDPOINT,

        aws_access_key_id=
            R2_ACCESS_KEY,

        aws_secret_access_key=
            R2_SECRET_KEY,

        region_name="auto",
    )


# ============================================================
# TEST R2 CONNECTION
# ============================================================

def test_connection():
    """
    Verify that PhotoBean can connect to
    the configured R2 bucket.
    """

    client = get_r2_client()


    print()
    print(
        "Testing Cloudflare R2 connection..."
    )

    print(
        f"Bucket: {R2_BUCKET}"
    )


    client.head_bucket(
        Bucket=R2_BUCKET
    )


    print(
        "Cloudflare R2 connection successful!"
    )


    return True


# ============================================================
# GENERATE SESSION ID
# ============================================================

def generate_session_id():
    """
    Generate a random PhotoBean session ID.

    Example:

    pb_abc123...
    """

    random_part = secrets.token_urlsafe(
        16
    )


    return (
        f"pb_{random_part}"
    )


# ============================================================
# CREATE GALLERY URL
# ============================================================

def get_gallery_url(
    session_id
):
    """
    Build the public gallery URL for
    a PhotoBean session.
    """

    return (
        f"{GALLERY_BASE_URL}"
        f"/p/{session_id}"
    )


# ============================================================
# UPLOAD ONE FILE
# ============================================================

def upload_file(
    local_file,
    r2_key
):
    """
    Upload one local file into the
    PhotoBean R2 bucket.
    """

    local_file = Path(
        local_file
    )


    # --------------------------------------------------------
    # Validate local file
    # --------------------------------------------------------

    if not local_file.exists():

        raise FileNotFoundError(
            "File does not exist: "
            f"{local_file}"
        )


    if not local_file.is_file():

        raise ValueError(
            "Path is not a file: "
            f"{local_file}"
        )


    # --------------------------------------------------------
    # Determine content type
    # --------------------------------------------------------

    content_type, _ = (
        mimetypes.guess_type(
            str(local_file)
        )
    )


    if content_type is None:

        content_type = (
            "application/octet-stream"
        )


    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------

    client = get_r2_client()


    print()
    print(
        "Uploading to Cloudflare R2..."
    )

    print(
        f"Local:  {local_file}"
    )

    print(
        f"R2:     {r2_key}"
    )


    client.upload_file(
        str(local_file),

        R2_BUCKET,

        r2_key,

        ExtraArgs={
            "ContentType":
                content_type
        }
    )


    print(
        "Upload complete."
    )


    return r2_key


# ============================================================
# UPLOAD COMPLETE PHOTO BEAN SESSION
# ============================================================

def upload_session(
    photo_paths,
    collage_path,
    session_id=None
):
    """
    Upload one complete PhotoBean session.

    Expected:

        3 original photos
        1 completed collage

    R2 structure:

        sessions/<session-id>/
            collage.jpg
            photo_1.jpg
            photo_2.jpg
            photo_3.jpg

    Returns:

        {
            "success": True,
            "session_id": "...",
            "gallery_url": "...",
            ...
        }
    """


    # --------------------------------------------------------
    # Validate photo count
    # --------------------------------------------------------

    if len(photo_paths) != 3:

        raise ValueError(
            "PhotoBean sessions require "
            "exactly 3 photos."
        )


    # --------------------------------------------------------
    # Convert paths
    # --------------------------------------------------------

    photos = [
        Path(path)
        for path in photo_paths
    ]


    collage_path = Path(
        collage_path
    )


    # --------------------------------------------------------
    # Validate original photos
    # --------------------------------------------------------

    for index, photo in enumerate(
        photos,
        start=1
    ):

        if not photo.exists():

            raise FileNotFoundError(
                f"Photo {index} "
                f"does not exist: "
                f"{photo}"
            )


        if not photo.is_file():

            raise ValueError(
                f"Photo {index} "
                f"is not a file: "
                f"{photo}"
            )


    # --------------------------------------------------------
    # Make sure all three paths are unique
    # --------------------------------------------------------

    unique_photo_paths = {
        str(
            photo.resolve()
        ).lower()
        for photo in photos
    }


    if len(unique_photo_paths) != 3:

        raise ValueError(
            "The session contains duplicate "
            "photo paths. PhotoBean requires "
            "3 different photos."
        )


    # --------------------------------------------------------
    # Validate collage
    # --------------------------------------------------------

    if not collage_path.exists():

        raise FileNotFoundError(
            "Collage does not exist: "
            f"{collage_path}"
        )


    if not collage_path.is_file():

        raise ValueError(
            "Collage path is not a file: "
            f"{collage_path}"
        )


    # --------------------------------------------------------
    # Generate session ID
    # --------------------------------------------------------

    if session_id is None:

        session_id = (
            generate_session_id()
        )


    # --------------------------------------------------------
    # Display session information
    # --------------------------------------------------------

    print()
    print(
        "=========================================="
    )

    print(
        "       PHOTO BEAN CLOUD SESSION"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Session ID:"
    )

    print(
        session_id
    )

    print()


    # --------------------------------------------------------
    # Session folder in R2
    # --------------------------------------------------------

    prefix = (
        f"sessions/"
        f"{session_id}"
    )


    # --------------------------------------------------------
    # Upload collage
    # --------------------------------------------------------

    collage_key = (
        f"{prefix}/collage.jpg"
    )


    upload_file(
        collage_path,
        collage_key
    )


    # --------------------------------------------------------
    # Upload original photos
    # --------------------------------------------------------

    photo_keys = []


    for index, photo in enumerate(
        photos,
        start=1
    ):

        photo_key = (
            f"{prefix}/"
            f"photo_{index}.jpg"
        )


        upload_file(
            photo,
            photo_key
        )


        photo_keys.append(
            photo_key
        )


    # --------------------------------------------------------
    # Generate public gallery URL
    # --------------------------------------------------------

    gallery_url = (
        get_gallery_url(
            session_id
        )
    )


    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print(
        "=========================================="
    )

    print(
        "SESSION UPLOAD COMPLETE"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Gallery:"
    )

    print(
        gallery_url
    )

    print()


    return {

        "success":
            True,

        "session_id":
            session_id,

        "gallery_url":
            gallery_url,

        "collage_key":
            collage_key,

        "photo_keys":
            photo_keys
    }


# ============================================================
# FIND THREE MOST RECENT UNIQUE PHOTOS
#
# THIS IS ONLY USED BY THE MANUAL TEST.
#
# The real PhotoBean application will pass
# session_photos directly into upload_session().
# ============================================================

def find_three_recent_photos():
    """
    Find the three most recently modified
    UNIQUE JPG/JPEG photos.

    This avoids the Windows duplicate problem
    caused by searching separately for:

        *.jpg
        *.JPG

    because Windows file matching is
    case-insensitive.
    """

    candidates = []


    # --------------------------------------------------------
    # Scan folder only once
    # --------------------------------------------------------

    for path in PHOTO_FOLDER.iterdir():

        if not path.is_file():
            continue


        # Only JPEG photos.

        if path.suffix.lower() not in (
            ".jpg",
            ".jpeg"
        ):

            continue


        # Do not accidentally use the
        # finished collage as a source photo.

        if path.name.lower() == (
            "latest_collage.jpg"
        ):

            continue


        candidates.append(
            path
        )


    # --------------------------------------------------------
    # Newest first
    # --------------------------------------------------------

    candidates.sort(
        key=lambda path:
            path.stat().st_mtime,
        reverse=True
    )


    # --------------------------------------------------------
    # Need at least three
    # --------------------------------------------------------

    if len(candidates) < 3:

        raise RuntimeError(
            "Could not find at least "
            "3 JPG/JPEG photos inside "
            "C:\\Photobooth\\Photos."
        )


    # --------------------------------------------------------
    # Take the three newest
    # --------------------------------------------------------

    selected = (
        candidates[:3]
    )


    # --------------------------------------------------------
    # Put them into capture order
    #
    # oldest = photo 1
    # middle = photo 2
    # newest = photo 3
    # --------------------------------------------------------

    selected.sort(
        key=lambda path:
            path.stat().st_mtime
    )


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    unique_paths = {
        str(
            path.resolve()
        ).lower()
        for path in selected
    }


    if len(unique_paths) != 3:

        raise RuntimeError(
            "Duplicate photos were detected "
            "during the manual session test."
        )


    return selected


# ============================================================
# MANUAL SESSION UPLOAD TEST
# ============================================================

def test_real_session_upload():
    """
    Test a complete PhotoBean session using
    the latest collage and three newest photos.

    This function is ONLY for manual testing.
    """


    collage_path = (
        PHOTO_FOLDER
        / "latest_collage.jpg"
    )


    # --------------------------------------------------------
    # Check collage
    # --------------------------------------------------------

    if not collage_path.exists():

        raise FileNotFoundError(
            "No collage was found at:\n"
            f"{collage_path}\n\n"
            "Run one PhotoBean session first."
        )


    # --------------------------------------------------------
    # Find test photos
    # --------------------------------------------------------

    photos = (
        find_three_recent_photos()
    )


    # --------------------------------------------------------
    # Show exactly what will upload
    # --------------------------------------------------------

    print()
    print(
        "Using these photos:"
    )

    print()


    for index, photo in enumerate(
        photos,
        start=1
    ):

        print(
            f"Photo {index}: "
            f"{photo.name}"
        )


    print()

    print(
        "Collage:"
    )

    print(
        collage_path.name
    )

    print()


    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------

    result = upload_session(
        photo_paths=photos,
        collage_path=collage_path
    )


    return result


# ============================================================
# RUN MANUAL TEST
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # Check R2
        # ----------------------------------------------------

        test_connection()


        # ----------------------------------------------------
        # Upload test session
        # ----------------------------------------------------

        result = (
            test_real_session_upload()
        )


        # ----------------------------------------------------
        # Show gallery URL
        # ----------------------------------------------------

        print()
        print(
            "OPEN THIS URL:"
        )

        print()

        print(
            result["gallery_url"]
        )

        print()


    except (
        BotoCoreError,
        ClientError
    ) as error:

        print()
        print(
            "Cloudflare R2 Error:"
        )

        print(
            error
        )


    except Exception as error:

        print()
        print(
            "PhotoBean Cloud Storage Error:"
        )

        print(
            error
        )


    input(
        "\nPress Enter to close..."
    )