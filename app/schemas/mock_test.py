from __future__ import annotations

from pydantic import BaseModel, Field


class MockTestSessionCreateRequest(BaseModel):
    difficulty: str
    currentStatus: str
    studentStatus: str
    livingSituation: str
    selectedLeisure: list[str]
    selectedHobbies: list[str]
    selectedExercises: list[str]
    selectedTravel: list[str]


class MockTestQuestionItem(BaseModel):
    id: int
    questionOrder: int
    questionType: str
    questionText: str


class MockTestSessionResponse(BaseModel):
    sessionId: int
    difficulty: str
    status: str
    questions: list[MockTestQuestionItem]


class MockTestAnswerItem(BaseModel):
    questionId: int
    transcript: str = ""
    durationSeconds: int = 0


class MockTestAnswerUpsertRequest(BaseModel):
    answers: list[MockTestAnswerItem]


class MockTestResultResponse(BaseModel):
    sessionId: int
    grade: str
    score: int
    breakdown: dict[str, int]
    summary: dict[str, str | int]
    strengths: list[str]
    improvements: list[str]
    categoryScores: list[dict[str, str | int]]
