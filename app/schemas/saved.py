from __future__ import annotations

from pydantic import BaseModel


class SavedQuestionCreateRequest(BaseModel):
    question: str
    answer: str
    category: str | None = None
    level: str | None = None
    questionIndex: int | None = None


class SavedQuestionItem(BaseModel):
    id: int
    question: str
    answer: str
    category: str | None
    level: str | None
    savedDate: str
    deleted: bool


class SavedQuestionListResponse(BaseModel):
    items: list[SavedQuestionItem]


class SavedPhraseCreateRequest(BaseModel):
    phrase: str
    meaning: str
    topic: str | None = None


class SavedPhraseItem(BaseModel):
    id: int
    phrase: str
    meaning: str
    topic: str | None


class SavedPhraseListResponse(BaseModel):
    items: list[SavedPhraseItem]


class SavedWordCreateRequest(BaseModel):
    topic: str
    word: str
    meaning: str


class SavedWordItem(BaseModel):
    id: int
    topic: str
    word: str
    meaning: str


class SavedWordListResponse(BaseModel):
    items: list[SavedWordItem]
