from __future__ import annotations

import json
import logging
import uuid
from typing import Any
from urllib import error, request

from fastapi import HTTPException

from app.config import STT_SERVICE_URL
from app.services.stt import transcribe_audio_payload

logger = logging.getLogger("opic-master-backend.stt-client")


def transcribe_with_fallback(
    *,
    audio_bytes: bytes,
    content_type: str | None,
    language: str,
    question_id: str | None = None,
) -> dict[str, Any]:
    remote_error: Exception | None = None

    if STT_SERVICE_URL:
        try:
            return _transcribe_via_http(
                audio_bytes=audio_bytes,
                content_type=content_type,
                language=language,
                question_id=question_id,
            )
        except Exception as exc:  # noqa: BLE001
            remote_error = exc
            logger.warning("Remote STT failed, falling back to local transcription: %s", exc)

    try:
        return transcribe_audio_payload(
            audio_bytes=audio_bytes,
            content_type=content_type,
            language=language,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        if remote_error is not None:
            raise HTTPException(
                status_code=503,
                detail=f"Both remote and local STT failed. remote={remote_error}; local={exc}",
            ) from exc
        raise


def _transcribe_via_http(
    *,
    audio_bytes: bytes,
    content_type: str | None,
    language: str,
    question_id: str | None,
) -> dict[str, Any]:
    boundary = f"----opic-{uuid.uuid4().hex}"
    content_type_value = content_type or "audio/webm"
    body = _build_multipart_body(
        boundary=boundary,
        fields={
            "language": language,
            "questionId": question_id or "",
        },
        file_field_name="audioFile",
        file_name="recording.webm",
        file_bytes=audio_bytes,
        file_content_type=content_type_value,
    )

    target_url = f"{STT_SERVICE_URL}/api/stt/transcriptions"
    req = request.Request(
        target_url,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(status_code=exc.code, detail=f"STT service request failed: {detail}") from exc
    except error.URLError as exc:
        raise HTTPException(status_code=503, detail=f"STT service is unreachable: {exc.reason}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Invalid STT response payload.")
    return payload


def _build_multipart_body(
    *,
    boundary: str,
    fields: dict[str, str],
    file_field_name: str,
    file_name: str,
    file_bytes: bytes,
    file_content_type: str,
) -> bytes:
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )

    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{file_field_name}"; '
                f'filename="{file_name}"\r\n'
            ).encode(),
            f"Content-Type: {file_content_type}\r\n\r\n".encode(),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )

    return b"".join(chunks)
