from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.stt import transcribe_audio_bytes

router = APIRouter(prefix="/api/stt", tags=["stt"])
logger = logging.getLogger("opic-master-backend.api.stt")


@router.post("/transcriptions")
async def transcribe_audio(
    audioFile: UploadFile = File(...),
    language: str = Form("en"),
    questionId: str | None = Form(None),
) -> dict[str, Any]:
    if not audioFile.content_type or not audioFile.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="audioFile must be an audio file.")

    audio_bytes = await audioFile.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audioFile must not be empty.")

    transcript = transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        content_type=audioFile.content_type,
        language=language,
    )

    logger.info(
        "Processed STT upload questionId=%s fileName=%s contentType=%s size=%s transcriptLength=%s",
        questionId,
        audioFile.filename,
        audioFile.content_type,
        len(audio_bytes),
        len(transcript),
    )

    return {
        "transcript": transcript,
        "language": language,
        "questionId": questionId,
        "provider": "faster-whisper",
        "fileName": audioFile.filename,
        "contentType": audioFile.content_type,
        "fileSize": len(audio_bytes),
    }
