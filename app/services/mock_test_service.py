from __future__ import annotations

import json
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.mock_test import MockTestAnswer, MockTestQuestion, MockTestResult, MockTestSession
from app.db.models.saved_content import StudyRecord
from app.schemas.mock_test import (
    MockTestAnswerUpsertRequest,
    MockTestQuestionItem,
    MockTestResultResponse,
    MockTestSessionCreateRequest,
    MockTestSessionResponse,
)

MOCK_QUESTIONS = [
    ("Self-Intro", "Let's start the interview now. Tell me about yourself."),
    ("Topic", "Tell me about your favorite cafe and why you like going there."),
    ("Topic", "Describe the atmosphere and interior of that cafe in detail."),
    ("Topic", "Tell me about a memorable experience you had at a cafe."),
    ("Topic", "Tell me about a recent trip you took. Where did you go?"),
    ("Topic", "What activities did you do during your trip?"),
    ("Topic", "Compare traveling now to traveling in the past."),
    ("Topic", "What kind of exercise do you do regularly?"),
    ("Topic", "Describe your exercise routine in detail."),
    ("Topic", "Tell me about a time when you achieved a fitness goal."),
    ("Role Play", "Your friend wants to join your gym. Call the gym and ask about membership options."),
    ("Role Play", "There's a problem with your membership. Call and explain the issue."),
    ("Role Play", "Suggest an alternative solution for the membership problem."),
    ("Follow-up", "Describe a challenge you faced recently and how you overcame it."),
    ("Follow-up", "What are your plans for the next few years?"),
]


class MockTestService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, payload: MockTestSessionCreateRequest) -> MockTestSessionResponse:
        session = MockTestSession(
            user_id=user_id,
            difficulty=payload.difficulty,
            current_status=payload.currentStatus,
            student_status=payload.studentStatus,
            living_situation=payload.livingSituation,
            selected_leisure=json.dumps(payload.selectedLeisure),
            selected_hobbies=json.dumps(payload.selectedHobbies),
            selected_exercises=json.dumps(payload.selectedExercises),
            selected_travel=json.dumps(payload.selectedTravel),
        )
        self.db.add(session)
        self.db.flush()

        for index, (question_type, question_text) in enumerate(MOCK_QUESTIONS, start=1):
            # TODO(USER): 이후에는 선택 정보 기반으로 실제 문제 생성 규칙을 넣어야 합니다.
            self.db.add(
                MockTestQuestion(
                    session_id=session.id,
                    question_order=index,
                    question_type=question_type,
                    question_text=question_text,
                )
            )

        self.db.commit()
        return self.get_session(session.id, user_id)

    def get_session(self, session_id: int, user_id: int) -> MockTestSessionResponse:
        session = self._get_session(session_id, user_id)
        questions = self.db.scalars(
            select(MockTestQuestion)
            .where(MockTestQuestion.session_id == session.id)
            .order_by(MockTestQuestion.question_order.asc())
        ).all()
        return MockTestSessionResponse(
            sessionId=session.id,
            difficulty=session.difficulty,
            status=session.status,
            questions=[
                MockTestQuestionItem(
                    id=question.id,
                    questionOrder=question.question_order,
                    questionType=question.question_type,
                    questionText=question.question_text,
                )
                for question in questions
            ],
        )

    def save_answers(
        self,
        session_id: int,
        user_id: int,
        payload: MockTestAnswerUpsertRequest,
    ) -> MockTestSessionResponse:
        session = self._get_session(session_id, user_id)
        existing = {
            answer.mock_test_question_id: answer
            for answer in self.db.scalars(select(MockTestAnswer).where(MockTestAnswer.session_id == session.id)).all()
        }
        for item in payload.answers:
            answer = existing.get(item.questionId)
            if answer is None:
                answer = MockTestAnswer(
                    session_id=session.id,
                    mock_test_question_id=item.questionId,
                    transcript=item.transcript,
                    duration_seconds=item.durationSeconds,
                )
                self.db.add(answer)
            else:
                answer.transcript = item.transcript
                answer.duration_seconds = item.durationSeconds
        self.db.commit()
        return self.get_session(session.id, user_id)

    def finish_session(self, session_id: int, user_id: int) -> MockTestResultResponse:
        session = self._get_session(session_id, user_id)
        answers = self.db.scalars(select(MockTestAnswer).where(MockTestAnswer.session_id == session.id)).all()
        answer_count = len([answer for answer in answers if answer.transcript.strip()])
        score = min(100, 55 + answer_count * 3)
        grade = "AL (Advanced Low)" if score >= 80 else "IH (Intermediate High)" if score >= 70 else "IM3 (Intermediate Mid)"

        result = self.db.scalar(select(MockTestResult).where(MockTestResult.session_id == session.id))
        if result is None:
            result = MockTestResult(
                session_id=session.id,
                grade=grade,
                score=score,
                breakdown_json=json.dumps({
                    "vocabulary": min(100, score + 3),
                    "grammar": max(60, score - 4),
                    "fluency": min(100, score + 2),
                    "pronunciation": max(60, score - 1),
                }),
                summary_json=json.dumps({
                    "totalQuestions": 15,
                    "averageResponseTime": "1분 45초",
                    "totalTime": "38분 23초",
                }),
                strengths_json=json.dumps([
                    "답변 구조가 비교적 안정적입니다.",
                    "자주 쓰는 표현을 무리 없이 연결합니다.",
                    "주제 전환이 크게 어색하지 않습니다.",
                ]),
                improvements_json=json.dumps([
                    "구체적인 예시를 조금 더 늘려보세요.",
                    "답변 첫 문장을 더 명확하게 시작하면 좋습니다.",
                    "연결 표현을 다양화할 여지가 있습니다.",
                ]),
                category_scores_json=json.dumps([
                    {"category": "자기소개", "score": min(100, score + 4)},
                    {"category": "주제 답변", "score": score},
                    {"category": "롤플레잉", "score": max(60, score - 3)},
                    {"category": "랜덤 질문", "score": max(60, score - 1)},
                ]),
            )
            self.db.add(result)
        else:
            result.grade = grade
            result.score = score

        session.status = "completed"
        session.completed_at = datetime.utcnow()

        self.db.add(
            StudyRecord(
                user_id=user_id,
                record_type="mock_test",
                source_id=session.id,
                grade=grade,
                score=score,
                duration_seconds=sum(answer.duration_seconds for answer in answers),
            )
        )
        self.db.commit()
        return self.get_result(session.id, user_id)

    def get_result(self, session_id: int, user_id: int) -> MockTestResultResponse:
        self._get_session(session_id, user_id)
        result = self.db.scalar(select(MockTestResult).where(MockTestResult.session_id == session_id))
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock test result not found.")
        return MockTestResultResponse(
            sessionId=session_id,
            grade=result.grade,
            score=result.score,
            breakdown=json.loads(result.breakdown_json),
            summary=json.loads(result.summary_json),
            strengths=json.loads(result.strengths_json),
            improvements=json.loads(result.improvements_json),
            categoryScores=json.loads(result.category_scores_json),
        )

    def _get_session(self, session_id: int, user_id: int) -> MockTestSession:
        session = self.db.scalar(
            select(MockTestSession).where(MockTestSession.id == session_id).where(MockTestSession.user_id == user_id)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock test session not found.")
        return session
