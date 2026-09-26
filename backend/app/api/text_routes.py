"""Text fake-news detection endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth_routes import get_current_user
from app.models.request_models import TextDetectionRequest
from app.models.response_models import DetectionResponse
from app.services.firebase_service import save_detection_result
from app.services.model_service import predict_text

router = APIRouter(prefix="/api/detect", tags=["Detection"])


@router.post("/text", response_model=DetectionResponse)
async def detect_text(
    request: TextDetectionRequest,
    user: dict = Depends(get_current_user),
) -> DetectionResponse:
    try:
        prediction = predict_text(request.text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Text model service failed") from exc

    record = save_detection_result(
        {
            "user_id": user["uid"],
            "file_name": None,
            "file_url": None,
            "storage_path": None,
            "detection_type": "text",
            "result": prediction["result"],
            "confidence": prediction["confidence"],
            "status": "completed",
            "created_at": datetime.now(timezone.utc),
        }
    )
    return DetectionResponse.from_record(record)