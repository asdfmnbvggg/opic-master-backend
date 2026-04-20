from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.saved_content import SavedPhrase, SavedQuestion, SavedWord
from app.schemas.saved import (
    SavedPhraseCreateRequest,
    SavedPhraseItem,
    SavedPhraseListResponse,
    SavedQuestionCreateRequest,
    SavedQuestionItem,
    SavedQuestionListResponse,
    SavedWordCreateRequest,
    SavedWordItem,
    SavedWordListResponse,
)


class SavedService:
    def __init__(self, db: Session):
        self.db = db

    def get_saved_questions(self, user_id: int) -> SavedQuestionListResponse:
        items = self.db.scalars(
            select(SavedQuestion).where(SavedQuestion.user_id == user_id).order_by(SavedQuestion.saved_at.desc())
        ).all()
        return SavedQuestionListResponse(items=[self._to_saved_question(item) for item in items])

    def save_question(self, user_id: int, payload: SavedQuestionCreateRequest) -> SavedQuestionListResponse:
        item = SavedQuestion(
            user_id=user_id,
            question_text=payload.question,
            answer_text=payload.answer,
            category=payload.category,
            level=payload.level,
            question_index=payload.questionIndex,
        )
        self.db.add(item)
        self.db.commit()
        return self.get_saved_questions(user_id)

    def delete_question(self, user_id: int, saved_id: int) -> SavedQuestionListResponse:
        item = self._get_question(user_id, saved_id)
        item.deleted_at = datetime.utcnow()
        self.db.commit()
        return self.get_saved_questions(user_id)

    def restore_question(self, user_id: int, saved_id: int) -> SavedQuestionListResponse:
        item = self._get_question(user_id, saved_id)
        item.deleted_at = None
        self.db.commit()
        return self.get_saved_questions(user_id)

    def get_saved_phrases(self, user_id: int) -> SavedPhraseListResponse:
        items = self.db.scalars(select(SavedPhrase).where(SavedPhrase.user_id == user_id)).all()
        return SavedPhraseListResponse(
            items=[SavedPhraseItem(id=item.id, phrase=item.phrase, meaning=item.meaning, topic=item.topic) for item in items]
        )

    def save_phrase(self, user_id: int, payload: SavedPhraseCreateRequest) -> SavedPhraseListResponse:
        self.db.add(SavedPhrase(user_id=user_id, phrase=payload.phrase, meaning=payload.meaning, topic=payload.topic))
        self.db.commit()
        return self.get_saved_phrases(user_id)

    def get_saved_words(self, user_id: int) -> SavedWordListResponse:
        items = self.db.scalars(select(SavedWord).where(SavedWord.user_id == user_id)).all()
        return SavedWordListResponse(
            items=[SavedWordItem(id=item.id, topic=item.topic, word=item.word, meaning=item.meaning) for item in items]
        )

    def save_word(self, user_id: int, payload: SavedWordCreateRequest) -> SavedWordListResponse:
        self.db.add(SavedWord(user_id=user_id, topic=payload.topic, word=payload.word, meaning=payload.meaning))
        self.db.commit()
        return self.get_saved_words(user_id)

    def _get_question(self, user_id: int, saved_id: int) -> SavedQuestion:
        item = self.db.scalar(
            select(SavedQuestion).where(SavedQuestion.user_id == user_id).where(SavedQuestion.id == saved_id)
        )
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved question not found.")
        return item

    @staticmethod
    def _to_saved_question(item: SavedQuestion) -> SavedQuestionItem:
        return SavedQuestionItem(
            id=item.id,
            question=item.question_text,
            answer=item.answer_text,
            category=item.category,
            level=item.level,
            savedDate=item.saved_at.strftime("%Y-%m-%d"),
            deleted=item.deleted_at is not None,
        )
