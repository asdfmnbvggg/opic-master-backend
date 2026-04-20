from __future__ import annotations

import os


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip() or default


STT_MODEL_SIZE = _get_env("STT_MODEL_SIZE", "base.en")
STT_DEVICE = _get_env("STT_DEVICE", "cpu")
STT_COMPUTE_TYPE = _get_env("STT_COMPUTE_TYPE", "int8")
BACKEND_HOST = _get_env("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(_get_env("BACKEND_PORT", "8000"))
CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
