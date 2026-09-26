"""Model integration boundary. Replace placeholders when trained models are available."""

from typing import TypedDict


class Prediction(TypedDict):
    result: str
    confidence: float


def predict_image(image_data: bytes) -> Prediction:
    """TODO: Connect the trained image/deepfake model here."""
    del image_data
    return {"result": "UNCERTAIN", "confidence": 0.0}


def predict_video(video_data: bytes) -> Prediction:
    """TODO: Connect the trained video/deepfake model here."""
    del video_data
    return {"result": "UNCERTAIN", "confidence": 0.0}


def predict_audio(audio_data: bytes) -> Prediction:
    """TODO: Connect the trained audio/deepfake model here."""
    del audio_data
    return {"result": "UNCERTAIN", "confidence": 0.0}


def predict_text(text: str) -> Prediction:
    """TODO: Connect the trained fake-news text model here."""
    del text
    return {"result": "UNCERTAIN", "confidence": 0.0}