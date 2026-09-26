"""Image detection endpoint."""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.auth_routes import get_current_user
from app.config import MAX_UPLOAD_SIZE_BYTES
from app.models.response_models import DetectionResponse
from app.services.firebase_service import save_detection_result
from app.services.model_service import predict_image
from app.services.storage_service import upload_file
from app.utils.file_validation import validate_uploaded_file

router = APIRouter(prefix="/api/detect", tags=["Detection"])


@router.post("/image", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
) -> DetectionResponse:
    file_data = await file.read(MAX_UPLOAD_SIZE_BYTES + 1)
    validate_uploaded_file(file.filename, file.content_type, len(file_data), "image")
    user_id = user["uid"]
    file_name = Path(file.filename or "upload").name
    stored_file = upload_file(user_id, file_name, file_data, "image")

    try:
        prediction = predict_image(file_data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Image model service failed") from exc

    created_at = datetime.now(timezone.utc)
    record = save_detection_result(
        {
            "user_id": user_id,
            "file_name": file_name,
            "file_url": stored_file["file_url"],
            "storage_path": stored_file["storage_path"],
            "detection_type": "image",
            "result": prediction["result"],
            "confidence": prediction["confidence"],
            "status": "completed",
            "created_at": created_at,
        }
    )
    return DetectionResponse.from_record(record)