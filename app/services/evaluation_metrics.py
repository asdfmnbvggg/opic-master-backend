from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

TOKEN_PATTERN = re.compile(r"[A-Za-z']+")
SENTENCE_SPLIT_PATTERN = re.compile(r"[.!?]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "why",
    "with",
    "you",
    "your",
}

FILLER_WORDS = {
    "ah",
    "er",
    "hmm",
    "like",
    "so",
    "uh",
    "uhm",
    "um",
    "well",
}


def compute_answer_metrics(
    *,
    question_text: str,
    used_transcript: str,
    audio_duration_seconds: float,
    transcript_confidence: float | None,
    segments: list[dict[str, Any]] | None = None,
) -> dict[str, float | int | bool]:
    normalized_transcript = used_transcript.strip()
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(normalized_transcript)]
    meaningful_tokens = [token for token in tokens if token not in STOPWORDS]
    sentences = [part.strip() for part in SENTENCE_SPLIT_PATTERN.split(normalized_transcript) if part.strip()]

    word_count = len(tokens)
    sentence_count = len(sentences) or (1 if normalized_transcript else 0)
    avg_sentence_length = round(word_count / sentence_count, 2) if sentence_count else 0.0

    repetition_rate = round(_calculate_repetition_rate(meaningful_tokens), 4)
    lexical_diversity = round((len(set(meaningful_tokens)) / len(meaningful_tokens)) if meaningful_tokens else 0.0, 4)
    keyword_similarity = round(_calculate_keyword_similarity(question_text, meaningful_tokens), 4)

    filler_count = sum(1 for token in tokens if token in FILLER_WORDS)
    filler_ratio = round((filler_count / word_count) if word_count else 0.0, 4)

    speech_duration_seconds, silence_duration_seconds, pause_count, avg_pause_seconds = _calculate_audio_metrics(
        audio_duration_seconds=audio_duration_seconds,
        word_count=word_count,
        segments=segments or [],
    )
    silence_ratio = round((silence_duration_seconds / audio_duration_seconds) if audio_duration_seconds > 0 else 0.0, 4)
    speech_rate_wpm = round((word_count / speech_duration_seconds) * 60, 2) if speech_duration_seconds > 0 else 0.0

    too_short = word_count < 20 or speech_duration_seconds < 15
    too_much_silence = silence_ratio >= 0.35 or (audio_duration_seconds >= 20 and speech_duration_seconds < 8)
    low_confidence = transcript_confidence is not None and transcript_confidence < 0.45
    is_gradable = not (too_short or too_much_silence or low_confidence)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "repetition_rate": repetition_rate,
        "lexical_diversity": lexical_diversity,
        "keyword_similarity": keyword_similarity,
        "speech_duration_seconds": round(speech_duration_seconds, 2),
        "silence_duration_seconds": round(silence_duration_seconds, 2),
        "silence_ratio": silence_ratio,
        "pause_count": pause_count,
        "avg_pause_seconds": round(avg_pause_seconds, 2),
        "speech_rate_wpm": speech_rate_wpm,
        "filler_count": filler_count,
        "filler_ratio": filler_ratio,
        "too_short": too_short,
        "too_much_silence": too_much_silence,
        "is_gradable": is_gradable,
    }


def _calculate_repetition_rate(tokens: list[str]) -> float:
    if not tokens:
        return 0.0

    counts = Counter(tokens)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return repeated / len(tokens)


def _calculate_keyword_similarity(question_text: str, transcript_tokens: list[str]) -> float:
    question_tokens = {
        token.lower()
        for token in TOKEN_PATTERN.findall(question_text)
        if token.lower() not in STOPWORDS
    }
    transcript_token_set = set(transcript_tokens)
    if not question_tokens:
        return 0.0
    overlap = len(question_tokens & transcript_token_set)
    return overlap / len(question_tokens)


def _calculate_audio_metrics(
    *,
    audio_duration_seconds: float,
    word_count: int,
    segments: list[dict[str, Any]],
) -> tuple[float, float, int, float]:
    if segments:
        speech_duration = 0.0
        pause_lengths: list[float] = []
        previous_end = 0.0

        for segment in segments:
            start = max(0.0, float(segment.get("start") or 0.0))
            end = max(start, float(segment.get("end") or start))
            speech_duration += max(0.0, end - start)
            pause = max(0.0, start - previous_end)
            if pause >= 0.4:
                pause_lengths.append(pause)
            previous_end = end

        silence_duration = max(0.0, audio_duration_seconds - speech_duration)
        pause_count = len(pause_lengths)
        avg_pause = sum(pause_lengths) / pause_count if pause_count else 0.0
        return speech_duration, silence_duration, pause_count, avg_pause

    estimated_speech_rate = 110.0
    estimated_speech_duration = (word_count / estimated_speech_rate) * 60 if word_count else 0.0
    speech_duration = min(max(estimated_speech_duration, 0.0), max(audio_duration_seconds, estimated_speech_duration))
    silence_duration = max(0.0, audio_duration_seconds - speech_duration)
    pause_count = max(0, math.floor(silence_duration / 2.5))
    avg_pause = silence_duration / pause_count if pause_count else 0.0
    return speech_duration, silence_duration, pause_count, avg_pause
