"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from firebase_admin.exceptions import FirebaseError
from google.api_core.exceptions import GoogleAPICallError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth_routes, audio_routes, history_routes, image_routes, text_routes, video_routes
from app.config import CORS_ORIGINS

app = FastAPI(
    title="AI Fake News & Deepfake Detector API",
    description="Backend integration API for media and text detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    del request
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": message},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid request",
            "details": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(FirebaseError)
async def firebase_exception_handler(request: Request, exc: FirebaseError) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": "Firebase service is unavailable"},
    )


@app.exception_handler(GoogleAPICallError)
async def google_api_exception_handler(
    request: Request,
    exc: GoogleAPICallError,
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": "Firebase service is unavailable"},
    )


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "success",
        "message": "AI Fake Detection Backend is running",
    }


app.include_router(auth_routes.router)
app.include_router(image_routes.router)
app.include_router(video_routes.router)
app.include_router(audio_routes.router)
app.include_router(text_routes.router)
app.include_router(history_routes.router)