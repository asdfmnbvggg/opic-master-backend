from __future__ import annotations

import json
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.practice import PracticeAnswer, PracticeFeedback, PracticeQuestion, PracticeQuestionSet, PracticeSession
from app.db.models.saved_content import StudyRecord
from app.schemas.practice import (
    PracticeEvaluationRequest,
    PracticeQuestionItem,
    PracticeQuestionSetCreateRequest,
    PracticeQuestionSetResponse,
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
)

PRACTICE_SEED_QUESTIONS = [
    {
        "category": "cafe",
        "difficulty": "5-6",
        "question_type": "topics",
        "text": "Tell me about your favorite cafe.",
        "translation": "가장 좋아하는 카페에 대해 말해보세요.",
        "hint": "location, atmosphere, menu, reason",
    },
    {
        "category": "travel",
        "difficulty": "5-6",
        "question_type": "topics",
        "text": "Describe a memorable travel experience.",
        "translation": "기억에 남는 여행 경험을 설명해보세요.",
        "hint": "where, with whom, what happened, feeling",
    },
    {
        "category": "exercise",
        "difficulty": "3-4",
        "question_type": "topics",
        "text": "What kind of exercise do you enjoy?",
        "translation": "어떤 운동을 즐기는지 말해보세요.",
        "hint": "type, frequency, reason, effect",
    },
]


class PracticeService:
    def __init__(self, db: Session):
        self.db = db
        self._ensure_seed_questions()

    def create_question_set(self, user_id: int, payload: PracticeQuestionSetCreateRequest) -> PracticeQuestionSetResponse:
        questions = self._select_questions(payload)
        question_set = PracticeQuestionSet(
            user_id=user_id,
            difficulty=payload.difficulty,
            question_type=payload.selectedType,
            selected_topics=json.dumps(payload.selectedTopics),
            question_ids=json.dumps([question.id for question in questions]),
        )
        self.db.add(question_set)
        self.db.commit()
        self.db.refresh(question_set)
        return self._build_question_set_response(question_set, questions)

    def get_question_set(self, question_set_id: int, user_id: int) -> PracticeQuestionSetResponse:
        question_set = self.db.scalar(
            select(PracticeQuestionSet)
            .where(PracticeQuestionSet.id == question_set_id)
            .where(PracticeQuestionSet.user_id == user_id)
        )
        if question_set is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found.")
        question_ids = json.loads(question_set.question_ids)
        questions = self.db.scalars(select(PracticeQuestion).where(PracticeQuestion.id.in_(question_ids))).all()
        return self._build_question_set_response(question_set, questions)

    def create_session(self, user_id: int, payload: PracticeSessionCreateRequest) -> PracticeSessionResponse:
        question_set = self.db.scalar(
            select(PracticeQuestionSet)
            .where(PracticeQuestionSet.id == payload.questionSetId)
            .where(PracticeQuestionSet.user_id == user_id)
        )
        if question_set is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question set not found.")
        session = PracticeSession(
            user_id=user_id,
            question_set_id=question_set.id,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return PracticeSessionResponse(
            sessionId=session.id,
            questionSetId=session.question_set_id,
            status=session.status,
            strengths=[],
            improvements=[],
            detailedFeedback=[],
        )

    def evaluate_session(
        self,
        session_id: int,
        user_id: int,
        payload: PracticeEvaluationRequest,
    ) -> PracticeSessionResponse:
        session = self._get_session(session_id, user_id)

        for item in payload.answers:
            answer = self.db.scalar(
                select(PracticeAnswer)
                .where(PracticeAnswer.session_id == session.id)
                .where(PracticeAnswer.question_id == item.questionId)
            )
            if answer is None:
                answer = PracticeAnswer(
                    session_id=session.id,
                    question_id=item.questionId,
                    question_order=item.questionOrder,
                    transcript=item.transcript,
                    edited_transcript=item.transcript,
                    duration_seconds=item.durationSeconds,
                )
                self.db.add(answer)
            else:
                answer.transcript = item.transcript
                answer.edited_transcript = item.transcript
                answer.duration_seconds = item.durationSeconds

        detailed_feedback = self._build_feedback(payload.answers)
        strengths = [
            "핵심 문장을 먼저 말하려는 흐름이 보입니다.",
            "주제와 관련된 기본 어휘 사용은 안정적입니다.",
            "답변 길이가 너무 짧지만 않다면 전달력은 충분합니다.",
        ]
        improvements = [
            "구체적인 예시를 1개씩만 더 추가해보세요.",
            "답변 첫 문장을 더 직접적으로 시작해보세요.",
            "because, for example 같은 연결 표현을 늘려보세요.",
        ]

        feedback = self.db.scalar(select(PracticeFeedback).where(PracticeFeedback.session_id == session.id))
        if feedback is None:
            feedback = PracticeFeedback(
                session_id=session.id,
                strengths_json=json.dumps(strengths),
                improvements_json=json.dumps(improvements),
                detailed_feedback_json=json.dumps(detailed_feedback),
            )
            self.db.add(feedback)
        else:
            feedback.strengths_json = json.dumps(strengths)
            feedback.improvements_json = json.dumps(improvements)
            feedback.detailed_feedback_json = json.dumps(detailed_feedback)

        session.status = "completed"
        session.completed_at = datetime.utcnow()
        self.db.add(
            StudyRecord(
                user_id=user_id,
                record_type="practice",
                source_id=session.id,
                grade="IH",
                score=min(100, 60 + len(payload.answers) * 5),
                duration_seconds=sum(item.durationSeconds for item in payload.answers),
            )
        )
        self.db.commit()
        return self.get_session_result(session.id, user_id)

    def get_session_result(self, session_id: int, user_id: int) -> PracticeSessionResponse:
        session = self._get_session(session_id, user_id)
        feedback = self.db.scalar(select(PracticeFeedback).where(PracticeFeedback.session_id == session.id))
        if feedback is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice feedback not found.")
        return PracticeSessionResponse(
            sessionId=session.id,
            questionSetId=session.question_set_id,
            status=session.status,
            strengths=json.loads(feedback.strengths_json),
            improvements=json.loads(feedback.improvements_json),
            detailedFeedback=json.loads(feedback.detailed_feedback_json),
        )

    def _get_session(self, session_id: int, user_id: int) -> PracticeSession:
        session = self.db.scalar(
            select(PracticeSession).where(PracticeSession.id == session_id).where(PracticeSession.user_id == user_id)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice session not found.")
        return session

    def _select_questions(self, payload: PracticeQuestionSetCreateRequest) -> list[PracticeQuestion]:
        query = select(PracticeQuestion)
        if payload.selectedType == "topics" and payload.selectedTopics:
            query = query.where(PracticeQuestion.category.in_(payload.selectedTopics))
        questions = self.db.scalars(query).all()
        if payload.selectedType == "random":
            return questions[:2]
        return questions

    @staticmethod
    def _build_question_set_response(
        question_set: PracticeQuestionSet,
        questions: list[PracticeQuestion],
    ) -> PracticeQuestionSetResponse:
        return PracticeQuestionSetResponse(
            questionSetId=question_set.id,
            difficulty=question_set.difficulty,
            selectedType=question_set.question_type,
            selectedTopics=json.loads(question_set.selected_topics),
            questions=[
                PracticeQuestionItem(
                    id=question.id,
                    category=question.category,
                    text=question.text,
                    translation=question.translation,
                    hint=question.hint,
                )
                for question in questions
            ],
        )

    @staticmethod
    def _build_feedback(answers: list) -> list[dict[str, object]]:
        feedback_items: list[dict[str, object]] = []
        for index, answer in enumerate(answers, start=1):
            transcript = answer.transcript.strip()
            word_count = len(transcript.split())
            # TODO(USER): 실제 채점 모델을 붙일 때는 이 규칙 기반 피드백을 LLM/평가 엔진 응답으로 교체하세요.
            feedback_items.append(
                {
                    "questionIndex": index,
                    "question": f"Question {index}",
                    "yourAnswer": transcript,
                    "feedbackPoints": [
                        {
                            "label": "Summary",
                            "text": "답변 길이가 적절합니다." if word_count >= 20 else "조금 더 길게 답해보면 좋습니다.",
                        },
                        {
                            "label": "Grammar",
                            "text": "기본 문장 구조는 유지되고 있습니다.",
                        },
                        {
                            "label": "Vocabulary",
                            "text": "반복 단어를 줄이고 유사 표현을 추가해보세요.",
                        },
                        {
                            "label": "Content",
                            "text": "이유와 예시를 함께 말하면 더 설득력 있어집니다.",
                        },
                    ],
                }
            )
        return feedback_items

    def _ensure_seed_questions(self) -> None:
        if self.db.scalar(select(PracticeQuestion.id).limit(1)) is not None:
            return
        for item in PRACTICE_SEED_QUESTIONS:
            # TODO(USER): 실제 서비스용 문제은행이 준비되면 이 시드 데이터는 교체하세요.
            self.db.add(PracticeQuestion(**item))
        self.db.commit()
