from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MockTestSession(Base):
    __tablename__ = "mock_test_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    difficulty: Mapped[str] = mapped_column(String(10))
    current_status: Mapped[str] = mapped_column(String(30))
    student_status: Mapped[str] = mapped_column(String(30))
    living_situation: Mapped[str] = mapped_column(String(30))
    selected_leisure: Mapped[str] = mapped_column(Text, default="[]")
    selected_hobbies: Mapped[str] = mapped_column(Text, default="[]")
    selected_exercises: Mapped[str] = mapped_column(Text, default="[]")
    selected_travel: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class MockTestQuestion(Base):
    __tablename__ = "mock_test_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("mock_test_sessions.id"), index=True)
    question_order: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(String(30))
    question_text: Mapped[str] = mapped_column(Text)


class MockTestAnswer(Base):
    __tablename__ = "mock_test_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("mock_test_sessions.id"), index=True)
    mock_test_question_id: Mapped[int] = mapped_column(ForeignKey("mock_test_questions.id"))
    transcript: Mapped[str] = mapped_column(Text, default="")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MockTestResult(Base):
    __tablename__ = "mock_test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("mock_test_sessions.id"), unique=True, index=True)
    grade: Mapped[str] = mapped_column(String(50))
    score: Mapped[int] = mapped_column(Integer)
    breakdown_json: Mapped[str] = mapped_column(Text, default="{}")
    summary_json: Mapped[str] = mapped_column(Text, default="{}")
    strengths_json: Mapped[str] = mapped_column(Text, default="[]")
    improvements_json: Mapped[str] = mapped_column(Text, default="[]")
    category_scores_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
