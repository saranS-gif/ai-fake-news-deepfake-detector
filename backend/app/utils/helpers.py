"""Small shared helpers for detection payloads."""

from typing import Any, Optional


def build_detection_record(
    *,
    user_id: str,
    detection_type: str,
    prediction: dict[str, Any],
    file_name: Optional[str] = None,
    file_url: Optional[str] = None,
    storage_path: Optional[str] = None,
) -> dict[str, Any]:
    """Build the Firestore fields shared by all detection routes."""
    from datetime import datetime, timezone

    return {
        "user_id": user_id,
        "file_name": file_name,
        "file_url": file_url,
        "storage_path": storage_path,
        "detection_type": detection_type,
        "result": prediction["result"],
        "confidence": prediction["confidence"],
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
    }