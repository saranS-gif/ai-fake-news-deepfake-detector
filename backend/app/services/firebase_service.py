"""Firebase Admin initialization and Firestore persistence operations."""

from datetime import datetime, timezone
from threading import Lock
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET

_initialization_lock = Lock()


def initialize_firebase() -> firebase_admin.App:
    """Initialize Firebase once, using application-default or configured credentials."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    with _initialization_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            options: dict[str, str] = {}
            if FIREBASE_PROJECT_ID:
                options["projectId"] = FIREBASE_PROJECT_ID
            if FIREBASE_STORAGE_BUCKET:
                options["storageBucket"] = FIREBASE_STORAGE_BUCKET

            credential_path = __import__("os").getenv("GOOGLE_APPLICATION_CREDENTIALS")
            credential = credentials.Certificate(credential_path) if credential_path else None
            return firebase_admin.initialize_app(credential, options or None)


def _database() -> firestore.Client:
    return firestore.client(app=initialize_firebase())


def save_user_profile(user_id: str, name: Optional[str], email: Optional[str]) -> None:
    """Create a profile document on first authenticated use without replacing its creation time."""
    profile = _database().collection("users").document(user_id)
    if not profile.get().exists:
        profile.set(
            {
                "name": name,
                "email": email,
                "created_at": firestore.SERVER_TIMESTAMP,
            }
        )


def save_detection_result(result: dict[str, Any]) -> dict[str, Any]:
    """Persist one detection record and return it with its generated document ID."""
    document = _database().collection("detection_results").document()
    payload = dict(result)
    payload["created_at"] = firestore.SERVER_TIMESTAMP
    document.set(payload)
    saved = document.get().to_dict() or result
    saved["result_id"] = document.id
    saved.setdefault("created_at", datetime.now(timezone.utc))
    return saved


def get_detection_result(result_id: str) -> Optional[dict[str, Any]]:
    """Return a detection result by document ID, or None when it does not exist."""
    snapshot = _database().collection("detection_results").document(result_id).get()
    if not snapshot.exists:
        return None
    result = snapshot.to_dict() or {}
    result["result_id"] = snapshot.id
    return result


def get_user_history(user_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """Return a user's newest detection results first."""
    query = (
        _database()
        .collection("detection_results")
        .where("user_id", "==", user_id)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    results = []
    for snapshot in query.stream():
        result = snapshot.to_dict() or {}
        result["result_id"] = snapshot.id
        results.append(result)
    return results