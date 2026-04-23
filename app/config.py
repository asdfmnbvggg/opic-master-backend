from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip() or default


def _default_sqlite_url() -> str:
    if os.name == "nt":
        local_app_data = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        db_dir = local_app_data / "opic-master-backend"
        db_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_dir.as_posix()}/opic_master.db"

    project_root = Path(__file__).resolve().parent.parent
    return f"sqlite:///{(project_root / 'opic_master.db').as_posix()}"


def _resolve_database_url(value: str) -> str:
    normalized = value.strip()
    if normalized.startswith("sqlite:///./"):
        return _default_sqlite_url()
    return normalized


STT_MODEL_SIZE = _get_env("STT_MODEL_SIZE", "base.en")
STT_DEVICE = _get_env("STT_DEVICE", "cpu")
STT_COMPUTE_TYPE = _get_env("STT_COMPUTE_TYPE", "int8")
BACKEND_HOST = _get_env("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(_get_env("BACKEND_PORT", "8000"))
PUBLIC_BACKEND_BASE_URL = _get_env("PUBLIC_BACKEND_BASE_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}").rstrip("/")
STT_SERVICE_URL = _get_env("STT_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
DATABASE_URL = _resolve_database_url(_get_env("DATABASE_URL", "sqlite:///./opic_master.db"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
APP_SECRET_KEY = _get_env("APP_SECRET_KEY", "change-me-in-production")
SMTP_HOST = _get_env("SMTP_HOST", "")
SMTP_PORT = int(_get_env("SMTP_PORT", "587"))
SMTP_USERNAME = _get_env("SMTP_USERNAME", "")
SMTP_PASSWORD = _get_env("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = _get_env("SMTP_FROM_EMAIL", "")
SMTP_USE_TLS = _get_env("SMTP_USE_TLS", "true").lower() == "true"
FRONTEND_BASE_URL = _get_env("FRONTEND_BASE_URL", "http://127.0.0.1:5173").rstrip("/")
CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

MEDIA_ROOT = Path(_get_env("MEDIA_ROOT", str((Path(__file__).resolve().parent.parent / "storage").as_posix())))
MEDIA_URL_PREFIX = _get_env("MEDIA_URL_PREFIX", "/media").rstrip("/") or "/media"
EVALUATION_AUDIO_DIR = MEDIA_ROOT / "evaluation-audio"
