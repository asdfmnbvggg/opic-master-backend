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

Run the command from the `opic-master-backend` directory.

## Local Setup

1. Copy `.env.example` to `.env`
2. Keep `DATABASE_URL=sqlite:///./opic_master.db` unless you intentionally want a custom database path
3. Start the backend from the `opic-master-backend` directory
4. Confirm the backend is running at `http://127.0.0.1:8000/health`

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
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_USE_TLS`

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
- Real email sending now uses SMTP settings from `.env`. If SMTP is not configured, email send requests will fail.
- The default SQLite setting is resolved to a writable local path automatically.
