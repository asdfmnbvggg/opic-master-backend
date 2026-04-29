from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.evaluation import EvaluationAnswer, EvaluationSession
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

    def _to_saved_question(self, item: SavedQuestion) -> SavedQuestionItem:
        metadata = self._find_question_metadata(item)
        return SavedQuestionItem(
            id=item.id,
            question=item.question_text,
            answer=item.answer_text,
            category=metadata.get("category") or item.category,
            level=item.level,
            hint=metadata.get("hint"),
            translation=metadata.get("translation"),
            savedDate=item.saved_at.strftime("%Y-%m-%d"),
            deleted=item.deleted_at is not None,
        )

    def _find_question_metadata(self, item: SavedQuestion) -> dict[str, str | None]:
        answer = self.db.scalar(
            select(EvaluationAnswer)
            .where(EvaluationAnswer.user_id == item.user_id)
            .where(EvaluationAnswer.question_text == item.question_text)
            .where(EvaluationAnswer.question_order == item.question_index)
            .order_by(EvaluationAnswer.updated_at.desc())
        )
        if answer is None:
            answer = self.db.scalar(
                select(EvaluationAnswer)
                .where(EvaluationAnswer.user_id == item.user_id)
                .where(EvaluationAnswer.question_text == item.question_text)
                .order_by(EvaluationAnswer.updated_at.desc())
        )
        if answer is None:
            return {"category": None, "hint": None, "translation": None}

        session = self.db.scalar(select(EvaluationSession).where(EvaluationSession.id == answer.session_id))
        metadata = self._deserialize_json(session.metadata_json if session else None, {})
        selected_type = metadata.get("selectedType") if isinstance(metadata.get("selectedType"), str) else None
        questions = metadata.get("questions", [])
        if not isinstance(questions, list):
            return {"category": None, "hint": None, "translation": None}

        for question in questions:
            if not isinstance(question, dict):
                continue
            if question.get("questionId") == answer.question_id or question.get("questionText") == item.question_text:
                question_category = question.get("category") if isinstance(question.get("category"), str) else None
                return {
                    "category": self._resolve_saved_category(selected_type, question_category, item.category),
                    "hint": question.get("hint") if isinstance(question.get("hint"), str) else None,
                    "translation": question.get("translation") if isinstance(question.get("translation"), str) else None,
                }

        return {"category": None, "hint": None, "translation": None}

    @staticmethod
    def _resolve_saved_category(
        selected_type: str | None,
        question_category: str | None,
        fallback_category: str | None,
    ) -> str | None:
        if selected_type == "topics":
            return question_category or fallback_category
        if selected_type == "random":
            return "돌발 문제"
        if selected_type == "roleplaying":
            return "롤플레잉"
        if fallback_category == "돌발문제":
            return "돌발 문제"
        return question_category or fallback_category

    @staticmethod
    def _deserialize_json(raw_value: str | None, default: Any) -> Any:
        if not raw_value:
            return default
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return default
