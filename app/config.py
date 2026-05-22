from __future__ import annotations

import os
import shutil
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
        data_root = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        db_dir = data_root / "opic-master-backend"
        db_path = db_dir / "opic_master.db"
        legacy_temp_db = Path(os.getenv("TEMP", data_root / "Temp")) / "opic-master-backend" / "opic_master.db"
        db_dir.mkdir(parents=True, exist_ok=True)
        if not db_path.exists() and legacy_temp_db.exists():
            shutil.copy2(legacy_temp_db, db_path)
        return f"sqlite:///{db_path.as_posix()}"

    project_root = Path(__file__).resolve().parent.parent
    return f"sqlite:///{(project_root / 'opic_master.db').as_posix()}"


def _resolve_database_url(value: str) -> str:
    normalized = value.strip()
    if normalized.startswith("sqlite:///./"):
        return _default_sqlite_url()
    return normalized


def _resolve_question_data_root(value: str) -> Path:
    if value.strip():
        return Path(value).expanduser().resolve()

    project_root = Path(__file__).resolve().parent.parent
    bundled_data_root = project_root / "question-data"
    if bundled_data_root.exists():
        return bundled_data_root

    return project_root.parent / "opic-master-data"


STT_MODEL_SIZE = _get_env("STT_MODEL_SIZE", "base.en")
STT_DEVICE = _get_env("STT_DEVICE", "cpu")
STT_COMPUTE_TYPE = _get_env("STT_COMPUTE_TYPE", "int8")
APP_ENV = _get_env("APP_ENV", "development").lower()
IS_DEVELOPMENT = APP_ENV in {"dev", "development", "local", "test"}
BACKEND_HOST = _get_env("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(_get_env("BACKEND_PORT", "8000"))
PUBLIC_BACKEND_BASE_URL = _get_env("PUBLIC_BACKEND_BASE_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}").rstrip("/")
STT_SERVICE_URL = _get_env("STT_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
DATABASE_URL = _resolve_database_url(_get_env("DATABASE_URL", "sqlite:///./opic_master.db"))
QUESTION_DATA_ROOT = _resolve_question_data_root(_get_env("QUESTION_DATA_ROOT", ""))
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
APP_SECRET_KEY = _get_env("APP_SECRET_KEY", "change-me-in-production")
if not IS_DEVELOPMENT and APP_SECRET_KEY == "change-me-in-production":
    raise RuntimeError("APP_SECRET_KEY must be set to a secure value outside development.")
SMTP_HOST = _get_env("SMTP_HOST", "")
SMTP_PORT = int(_get_env("SMTP_PORT", "587"))
SMTP_USERNAME = _get_env("SMTP_USERNAME", "")
SMTP_PASSWORD = _get_env("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = _get_env("SMTP_FROM_EMAIL", "")
SMTP_USE_TLS = _get_env("SMTP_USE_TLS", "true").lower() == "true"
RESEND_API_KEY = _get_env("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = _get_env("RESEND_FROM_EMAIL", "")
FRONTEND_BASE_URL = _get_env("FRONTEND_BASE_URL", "http://127.0.0.1:5173").rstrip("/")
CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,capacitor://localhost,http://localhost,https://localhost,ionic://localhost",
    ).split(",")
    if origin.strip()
]

MEDIA_ROOT = Path(_get_env("MEDIA_ROOT", str((Path(__file__).resolve().parent.parent / "storage").as_posix())))
MEDIA_URL_PREFIX = _get_env("MEDIA_URL_PREFIX", "/media").rstrip("/") or "/media"
EVALUATION_AUDIO_DIR = MEDIA_ROOT / "evaluation-audio"
SAVE_EVALUATION_AUDIO = _get_env("SAVE_EVALUATION_AUDIO", "false").lower() == "true"
SERVE_MEDIA_FILES = _get_env("SERVE_MEDIA_FILES", "false").lower() == "true"
