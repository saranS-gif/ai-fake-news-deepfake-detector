# AI Fake News & Deepfake Detector Backend

FastAPI integration layer between the frontend, Firebase Authentication, Cloud Firestore, Firebase Storage, and separately trained detection models. The model functions currently return `UNCERTAIN` with zero confidence; no AI model is included or trained here.

## Architecture

```text
React frontend -> FastAPI routes -> Firebase services (Auth, Firestore, Storage)
                              \-> model_service.py -> teammate's trained models
```

All detection and history endpoints require a Firebase ID token in the `Authorization: Bearer <token>` header. The backend derives `user_id` from the verified token. Uploaded media is stored in Firebase Storage; Firestore contains metadata and the result, not the media bytes.

## Folder structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── image_routes.py
│   │   ├── video_routes.py
│   │   ├── audio_routes.py
│   │   ├── text_routes.py
│   │   ├── auth_routes.py
│   │   └── history_routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── firebase_service.py
│   │   ├── storage_service.py
│   │   └── model_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py
│   │   └── response_models.py
│   └── utils/
│       ├── __init__.py
│       ├── file_validation.py
│       └── helpers.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

`main.py` configures FastAPI, CORS, health, and error responses. `api/` validates requests and coordinates services. `services/` contains Firebase, Storage, and model integration. `models/` defines Pydantic schemas. `utils/` contains media validation and shared record construction. `.env.example` documents configuration; `.gitignore` excludes local secrets and Python artifacts.

## Install and run

From the repository root in PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

On macOS/Linux, activate with `source .venv/bin/activate`. The API runs at `http://127.0.0.1:8000`; Swagger UI is at `http://127.0.0.1:8000/docs`.

## Firebase setup

1. Create a Firebase project and enable Authentication (the frontend should sign users in with Firebase Authentication).
2. Create a Cloud Firestore database and a Firebase Storage bucket.
3. In Firebase project settings, note the project ID and Storage bucket name.
4. Create a service account key for local development. Keep the downloaded JSON out of source control and place it at `backend/firebase-key.json`.
5. Set `FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, and `GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json` in `backend/.env`. On deployed infrastructure, prefer Application Default Credentials or the platform's service identity instead of committing a key.
6. Set `CORS_ORIGINS` to the exact frontend origins (comma-separated), and adjust `MAX_UPLOAD_SIZE_MB` if needed.

The Firebase Admin SDK initializes lazily on the first authenticated/Firebase-backed request. The health endpoint and Swagger can run without Firebase credentials.

Firestore collection: `detection_results/{result_id}` contains `user_id`, `file_name`, `file_url`, `storage_path`, `detection_type`, `result`, `confidence`, `status`, and `created_at`. Text detections have null file fields. Uploaded object paths use `uploads/{user_id}/{images|videos|audio}/...`. A profile document with `name`, `email`, and `created_at` is created in `users/{user_id}` on the first successful token verification.

## API endpoints

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health` | None | Health status |
| POST | `/api/auth/verify` | ID token in JSON body | Verify a Firebase ID token |
| POST | `/api/detect/image` | Bearer ID token | Upload and record image detection |
| POST | `/api/detect/video` | Bearer ID token | Upload and record placeholder video detection |
| POST | `/api/detect/audio` | Bearer ID token | Upload and record placeholder audio detection |
| POST | `/api/detect/text` | Bearer ID token | Record placeholder text detection |
| GET | `/api/history/{user_id}` | Bearer ID token | List the caller's history (`limit` 1-500, default 100) |
| GET | `/api/result/{result_id}` | Bearer ID token | Fetch one caller-owned result |

The frontend should obtain an ID token using the Firebase client SDK and send it as `Authorization: Bearer <id-token>`. For file routes, use `multipart/form-data` with a `file` field. Accepted extensions are JPG/JPEG, PNG, WEBP; MP4, MOV, WEBM; and MP3, WAV, M4A, OGG. Maximum size is configured by `MAX_UPLOAD_SIZE_MB`.

## Example requests and responses

Health:

```http
GET /api/health
```

```json
{"status":"success","message":"AI Fake Detection Backend is running"}
```

Text detection (include the caller's Firebase ID token):

```bash
curl -X POST http://127.0.0.1:8000/api/detect/text \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"News content here"}'
```

```json
{
  "success": true,
  "result_id": "abc123",
  "detection_type": "text",
  "result": "UNCERTAIN",
  "confidence": 0.0,
  "file_url": null,
  "created_at": "2026-09-26T12:00:00Z"
}
```

Image upload:

```bash
curl -X POST http://127.0.0.1:8000/api/detect/image \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -F "file=@./sample.jpg"
```

The response has the same fields, with `detection_type` set to `image` and `file_url` set to its Firebase Storage download URL. Invalid file types return HTTP 415, oversized files HTTP 413, invalid requests HTTP 422, and Firebase failures HTTP 503, all with a JSON `success: false` error body.

## Model handoff

The ML teammate should connect their trained model in exactly these functions in `app/services/model_service.py`: `predict_image(image_data)`, `predict_video(video_data)`, `predict_audio(audio_data)`, and `predict_text(text)`. Each must return `{"result": "REAL" | "FAKE" | "AI_GENERATED" | "UNCERTAIN", "confidence": 0.0..1.0}`. Keep loading and inference in this service; route modules should remain model-agnostic.