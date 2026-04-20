from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, APP_SECRET_KEY


def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        200_000,
    ).hex()
    return f"{salt_value}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_value, _ = stored_hash.split("$", maxsplit=1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt_value), stored_hash)


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "exp": int((datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(APP_SECRET_KEY.encode("utf-8"), body, hashlib.sha256).digest()
    return f"{base64.urlsafe_b64encode(body).decode('utf-8')}.{base64.urlsafe_b64encode(signature).decode('utf-8')}"


def decode_access_token(token: str) -> dict[str, int] | None:
    try:
        body_b64, signature_b64 = token.split(".", maxsplit=1)
        body = base64.urlsafe_b64decode(body_b64.encode("utf-8"))
        signature = base64.urlsafe_b64decode(signature_b64.encode("utf-8"))
        expected = hmac.new(APP_SECRET_KEY.encode("utf-8"), body, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(body.decode("utf-8"))
        if payload["exp"] < int(datetime.now(UTC).timestamp()):
            return None
        return payload
    except Exception:
        return None
