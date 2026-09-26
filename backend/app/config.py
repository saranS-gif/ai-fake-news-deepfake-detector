"""Environment-backed application configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


def _read_origins() -> tuple[str, ...]:
    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    )
    return tuple(origin.strip() for origin in origins.split(",") if origin.strip())


FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")
CORS_ORIGINS = _read_origins()
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
HISTORY_DEFAULT_LIMIT = 100
HISTORY_MAX_LIMIT = 500

ALLOWED_FILE_TYPES = {
    "image": {
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".png": {"image/png"},
        ".webp": {"image/webp"},
    },
    "video": {
        ".mp4": {"video/mp4"},
        ".mov": {"video/quicktime"},
        ".webm": {"video/webm"},
    },
    "audio": {
        ".mp3": {"audio/mpeg", "audio/mp3"},
        ".wav": {"audio/wav", "audio/x-wav"},
        ".m4a": {"audio/mp4", "audio/x-m4a"},
        ".ogg": {"audio/ogg", "application/ogg"},
    },
}