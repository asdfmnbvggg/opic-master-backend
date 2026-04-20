# OPIc Master Backend

FastAPI backend for the OPIc Master frontend.

## Features

- Health check endpoint
- Speech-to-text upload endpoint using `faster-whisper`
- Environment-based CORS and runtime configuration

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

## API

- `GET /health`
- `POST /api/stt/transcriptions`
