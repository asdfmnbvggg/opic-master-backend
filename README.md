# OPIc Master Backend

FastAPI backend for the OPIc Master frontend.

## Features

- Health check endpoint
- Speech-to-text upload endpoint using `faster-whisper`
- Environment-based CORS and runtime configuration
- SQLite-based auth / practice / mock test / saved / records API scaffold

## Local Run

```bash
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Environment Variables

Copy `.env.example` to `.env` if you want to manage values locally.

- `STT_MODEL_SIZE`
- `STT_DEVICE`
- `STT_COMPUTE_TYPE`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `CORS_ALLOW_ORIGINS`
- `DATABASE_URL`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `APP_SECRET_KEY`

## API

- `GET /health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/find-id`
- `POST /api/auth/reset-password/request`
- `POST /api/auth/reset-password/confirm`
- `POST /api/stt/transcriptions`
- `POST /api/practice/question-sets`
- `POST /api/mock-tests/sessions`
- `GET /api/saved/questions`
- `GET /api/records/dashboard`

## Notes

- `TODO(USER)` comments mark places where your project-specific policy or external integration should be added.
- The current evaluation logic is rule-based placeholder logic so the frontend can be connected first.
