from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EvaluationSession(Base):
    __tablename__ = "evaluation_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", index=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    completed_questions: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    overall_strengths_json: Mapped[str] = mapped_column(Text, default="[]")
    overall_weaknesses_json: Mapped[str] = mapped_column(Text, default="[]")
    overall_feedback_json: Mapped[str] = mapped_column(Text, default="{}")
    overall_tips_json: Mapped[str] = mapped_column(Text, default="[]")
    category_scores_json: Mapped[str] = mapped_column(Text, default="{}")
    estimated_grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_gradable: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class EvaluationAnswer(Base):
    __tablename__ = "evaluation_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_evaluation_answers_session_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("evaluation_sessions.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20), index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    question_order: Mapped[int] = mapped_column(Integer, default=1)
    question_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    question_text: Mapped[str] = mapped_column(Text)
    audio_file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    original_transcript: Mapped[str] = mapped_column(Text, default="")
    edited_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    used_transcript: Mapped[str] = mapped_column(Text, default="")
    transcript_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    stt_segments_json: Mapped[str] = mapped_column(Text, default="[]")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    sentence_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_sentence_length: Mapped[float] = mapped_column(Float, default=0.0)
    repetition_rate: Mapped[float] = mapped_column(Float, default=0.0)
    lexical_diversity: Mapped[float] = mapped_column(Float, default=0.0)
    keyword_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    speech_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    silence_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    silence_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    pause_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_pause_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    speech_rate_wpm: Mapped[float] = mapped_column(Float, default=0.0)
    filler_count: Mapped[int] = mapped_column(Integer, default=0)
    filler_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    too_short: Mapped[bool] = mapped_column(Boolean, default=False)
    too_much_silence: Mapped[bool] = mapped_column(Boolean, default=False)
    is_gradable: Mapped[bool] = mapped_column(Boolean, default=True)
    feedback_json: Mapped[str] = mapped_column(Text, default="{}")
    estimated_sub_grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
