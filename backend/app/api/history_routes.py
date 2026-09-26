"""Detection history and single-result endpoints."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.auth_routes import get_current_user
from app.config import HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT
from app.models.response_models import DetectionResponse, HistoryResponse
from app.services.firebase_service import get_detection_result, get_user_history

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history/{user_id}", response_model=HistoryResponse)
async def detection_history(
    user_id: str,
    limit: int = Query(default=HISTORY_DEFAULT_LIMIT, ge=1, le=HISTORY_MAX_LIMIT),
    user: dict = Depends(get_current_user),
) -> HistoryResponse:
    if user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="You can only access your own history")
    results = get_user_history(user_id, limit=limit)
    return HistoryResponse(success=True, results=[DetectionResponse.from_record(row) for row in results])


@router.get("/result/{result_id}", response_model=DetectionResponse)
async def detection_result(
    result_id: str,
    user: dict = Depends(get_current_user),
) -> DetectionResponse:
    result: Optional[dict[str, Any]] = get_detection_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Detection result not found")
    if result.get("user_id") != user["uid"]:
        raise HTTPException(status_code=403, detail="You can only access your own results")
    return DetectionResponse.from_record(result)