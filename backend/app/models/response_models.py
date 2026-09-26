"""Validated API response schemas."""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

DetectionType = Literal["image", "video", "audio", "text"]
DetectionLabel = Literal["REAL", "FAKE", "AI_GENERATED", "UNCERTAIN"]


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool
    result_id: str
    detection_type: DetectionType
    result: DetectionLabel
    confidence: float = Field(ge=0.0, le=1.0)
    file_url: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_record(cls, record: dict) -> "DetectionResponse":
        return cls(
            success=True,
            result_id=record["result_id"],
            detection_type=record["detection_type"],
            result=record["result"],
            confidence=record["confidence"],
            file_url=record.get("file_url"),
            created_at=record.get("created_at") or datetime.now(timezone.utc),
        )


class HistoryResponse(BaseModel):
    success: bool
    results: list[DetectionResponse]


class AuthResponse(BaseModel):
    success: bool
    user_id: str
    email: Optional[str] = None