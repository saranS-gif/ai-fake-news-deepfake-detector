"""Firebase Storage upload, URL, and deletion operations."""

from pathlib import Path
from typing import Optional
from urllib.parse import quote
from uuid import uuid4

from firebase_admin import storage

from app.services.firebase_service import initialize_firebase


def upload_file(
    user_id: str,
    file_name: str,
    file_data: bytes,
    detection_type: str,
) -> dict[str, str]:
    """Upload bytes to a user-scoped Firebase Storage path."""
    app = initialize_firebase()
    bucket = storage.bucket(app=app)
    safe_name = Path(file_name).name
    folder = {"image": "images", "video": "videos", "audio": "audio"}[detection_type]
    storage_path = f"uploads/{user_id}/{folder}/{uuid4().hex}-{safe_name}"
    blob = bucket.blob(storage_path)
    blob.upload_from_string(file_data)
    download_token = uuid4().hex
    blob.metadata = {"firebaseStorageDownloadTokens": download_token}
    blob.patch()
    return {
        "storage_path": storage_path,
        "file_url": get_file_url(storage_path, download_token),
    }


def get_file_url(storage_path: str, download_token: Optional[str] = None) -> str:
    """Build a Firebase Storage download URL using the stored download token."""
    app = initialize_firebase()
    bucket = storage.bucket(app=app)
    blob = bucket.blob(storage_path)
    if download_token is None:
        blob.reload()
        metadata = blob.metadata or {}
        download_token = metadata.get("firebaseStorageDownloadTokens")
    if not download_token:
        raise ValueError("Storage object does not have a Firebase download token")
    encoded_path = quote(storage_path, safe="")
    return (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
        f"{encoded_path}?alt=media&token={download_token}"
    )


def delete_file(storage_path: str) -> None:
    """Delete a stored object by its bucket-relative path."""
    app = initialize_firebase()
    storage.bucket(app=app).blob(storage_path).delete()