"""Upload validation for media type, extension, and configured size limits."""

from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from app.config import ALLOWED_FILE_TYPES, MAX_UPLOAD_SIZE_BYTES, MAX_UPLOAD_SIZE_MB


def validate_uploaded_file(
    file_name: Optional[str],
    content_type: Optional[str],
    file_size: int,
    detection_type: str,
) -> None:
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large; maximum size is {MAX_UPLOAD_SIZE_MB} MB",
        )
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    extension = Path(file_name or "").suffix.lower()
    accepted_types = ALLOWED_FILE_TYPES.get(detection_type, {})
    if extension not in accepted_types:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    normalized_type = (content_type or "").split(";", maxsplit=1)[0].strip().lower()
    if normalized_type and normalized_type != "application/octet-stream":
        if normalized_type not in accepted_types[extension]:
            raise HTTPException(status_code=415, detail="File content type does not match its extension")