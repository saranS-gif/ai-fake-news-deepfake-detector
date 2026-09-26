"""Validated request schemas."""

from pydantic import BaseModel, Field


class TextDetectionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class TokenVerificationRequest(BaseModel):
    id_token: str = Field(min_length=1)