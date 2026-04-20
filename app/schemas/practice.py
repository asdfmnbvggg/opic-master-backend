from __future__ import annotations

from pydantic import BaseModel


class PracticeQuestionSetCreateRequest(BaseModel):
    difficulty: str
    selectedType: str
    selectedTopics: list[str] = []


class PracticeQuestionItem(BaseModel):
    id: int
    category: str
    text: str
    translation: str
    hint: str


class PracticeQuestionSetResponse(BaseModel):
    questionSetId: int
    difficulty: str
    selectedType: str
    selectedTopics: list[str]
    questions: list[PracticeQuestionItem]


class PracticeSessionCreateRequest(BaseModel):
    questionSetId: int


class PracticeAnswerItem(BaseModel):
    questionId: int
    questionOrder: int
    transcript: str = ""
    durationSeconds: int = 0


class PracticeEvaluationRequest(BaseModel):
    answers: list[PracticeAnswerItem]


class PracticeSessionResponse(BaseModel):
    sessionId: int
    questionSetId: int
    status: str
    strengths: list[str]
    improvements: list[str]
    detailedFeedback: list[dict[str, object]]
