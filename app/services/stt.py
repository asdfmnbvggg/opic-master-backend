from __future__ import annotations

import logging
import os
import tempfile
from functools import lru_cache

from fastapi import HTTPException
from faster_whisper import WhisperModel

from app.config import STT_COMPUTE_TYPE, STT_DEVICE, STT_MODEL_SIZE

logger = logging.getLogger("opic-master-backend.stt")


@lru_cache(maxsize=1)
def get_whisper_model() -> WhisperModel:
    logger.info(
        "Loading faster-whisper model model_size=%s device=%s compute_type=%s",
        STT_MODEL_SIZE,
        STT_DEVICE,
        STT_COMPUTE_TYPE,
    )
    return WhisperModel(
        STT_MODEL_SIZE,
        device=STT_DEVICE,
        compute_type=STT_COMPUTE_TYPE,
    )


def transcribe_audio_bytes(audio_bytes: bytes, content_type: str | None, language: str) -> str:
    suffix = guess_file_suffix(content_type)
    normalized_language = normalize_language(language)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        model = get_whisper_model()
        segments, info = model.transcribe(
            temp_audio_path,
            beam_size=5,
            language=normalized_language,
            vad_filter=True,
        )
        segment_list = list(segments)
        transcript = " ".join(
            segment.text.strip()
            for segment in segment_list
            if segment.text and segment.text.strip()
        ).strip()

        logger.info(
            "faster-whisper completed language=%s probability=%.4f segments=%s",
            info.language,
            info.language_probability,
            len(segment_list),
        )

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail="Speech was detected but no transcript was produced.",
            )

        return transcript
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("faster-whisper transcription failed")
        raise HTTPException(status_code=500, detail=f"STT transcription failed: {exc}") from exc
    finally:
        try:
            os.remove(temp_audio_path)
        except OSError:
            logger.warning("Failed to remove temporary audio file: %s", temp_audio_path)


def normalize_language(language: str | None) -> str:
    if not language:
        return "en"

    normalized = language.strip().lower()
    if normalized in {"english", "en-us", "en-gb"}:
        return "en"
    return normalized or "en"


def guess_file_suffix(content_type: str | None) -> str:
    if not content_type:
        return ".webm"

    if "ogg" in content_type:
        return ".ogg"
    if "mp4" in content_type or "m4a" in content_type:
        return ".mp4"
    if "wav" in content_type:
        return ".wav"
    if "mpeg" in content_type or "mp3" in content_type:
        return ".mp3"
    return ".webm"
