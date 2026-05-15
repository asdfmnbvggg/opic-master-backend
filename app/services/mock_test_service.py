from __future__ import annotations

import json
import random
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import QUESTION_DATA_ROOT
from app.db.models.mock_test import MockTestAnswer, MockTestQuestion, MockTestResult, MockTestSession
from app.db.models.saved_content import StudyRecord
from app.schemas.mock_test import (
    MockTestAnswerUpsertRequest,
    MockTestQuestionItem,
    MockTestResultResponse,
    MockTestSessionCreateRequest,
    MockTestSessionResponse,
)

DATA_ROOT = QUESTION_DATA_ROOT
MOCK_TEST_QUESTION_COUNT = 15

SELF_INTRO_QUESTION = {
    "questionType": "Self-Intro",
    "questionText": "Let's start the interview now. Tell me about yourself.",
    "translation": "이제 인터뷰를 시작하겠습니다. 자기소개를 해주세요.",
    "hint": "name, work or school, daily routine, hobbies, personality",
    "category": "자기소개",
}

TOPIC_NAME_MAP = {
    "영화": "영화",
    "공연": "공연",
    "콘서트": "공연",
    "술집/바": "술집",
    "공원": "공원",
    "캠핑": "캠핑",
    "요리": "요리",
    "게임": "게임",
    "SNS": "SNS",
    "카페": "카페",
    "쇼핑": "쇼핑",
    "음악 감상": "음악",
    "혼자 노래 부르기": "음악",
    "악기 연주": "음악",
    "걷기": "조깅산책",
    "조깅": "조깅산책",
    "헬스": "운동",
    "운동 수업 수강": "운동",
    "운동안함": "운동",
    "하이킹": "산",
    "국내 여행": "국내여행",
    "국내 출장": "국내여행",
    "해외 여행": "해외여행",
    "해외 출장": "해외여행",
    "집에서 보내는 휴가": "휴일",
    "주거 개선": "집",
    "구직활동": "구직",
}


class MockTestService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, payload: MockTestSessionCreateRequest) -> MockTestSessionResponse:
        generated_questions = self._build_mock_questions(payload)
        session = MockTestSession(
            user_id=user_id,
            difficulty=payload.difficulty,
            current_status=payload.currentStatus,
            student_status=payload.studentStatus,
            living_situation=payload.livingSituation,
            selected_leisure=json.dumps(payload.selectedLeisure, ensure_ascii=False),
            selected_hobbies=json.dumps(payload.selectedHobbies, ensure_ascii=False),
            selected_exercises=json.dumps(payload.selectedExercises, ensure_ascii=False),
            selected_travel=json.dumps(payload.selectedTravel, ensure_ascii=False),
        )
        self.db.add(session)
        self.db.flush()

        response_questions: list[MockTestQuestionItem] = []
        for index, question in enumerate(generated_questions, start=1):
            db_question = MockTestQuestion(
                session_id=session.id,
                question_order=index,
                question_type=question["questionType"],
                question_text=question["questionText"],
            )
            self.db.add(db_question)
            self.db.flush()
            response_questions.append(
                MockTestQuestionItem(
                    id=db_question.id,
                    questionOrder=index,
                    questionType=question["questionType"],
                    questionText=question["questionText"],
                    translation=question.get("translation", ""),
                    hint=question.get("hint", ""),
                    category=question.get("category", ""),
                )
            )

        self.db.commit()
        return MockTestSessionResponse(
            sessionId=session.id,
            difficulty=session.difficulty,
            status=session.status,
            questions=response_questions,
        )

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
                    category=question.question_type,
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
                    "totalQuestions": MOCK_TEST_QUESTION_COUNT,
                    "averageResponseTime": "1분 45초",
                    "totalTime": "38분 23초",
                }, ensure_ascii=False),
                strengths_json=json.dumps([
                    "답변 구조가 비교적 안정적입니다.",
                    "자주 쓰는 표현을 자연스럽게 연결했습니다.",
                    "주제 전환이 크게 어색하지 않았습니다.",
                ], ensure_ascii=False),
                improvements_json=json.dumps([
                    "구체적인 예시를 조금 더 늘려보세요.",
                    "답변 첫 문장을 더 명확하게 시작하면 좋습니다.",
                    "연결 표현을 다양하게 사용해보세요.",
                ], ensure_ascii=False),
                category_scores_json=json.dumps([
                    {"category": "자기소개", "score": min(100, score + 4)},
                    {"category": "주제 답변", "score": score},
                    {"category": "롤플레잉", "score": max(60, score - 3)},
                    {"category": "돌발 질문", "score": max(60, score - 1)},
                ], ensure_ascii=False),
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

    def _build_mock_questions(self, payload: MockTestSessionCreateRequest) -> list[dict[str, str]]:
        level_prefix = self._resolve_level_prefix(payload.difficulty)
        topic_questions = self._load_grouped_topic_questions(
            level_prefix,
            self._resolve_selected_topics(payload),
        )
        roleplay_questions = self._load_questions_from_file(
            DATA_ROOT / f"{level_prefix}_롤플레잉.json",
            "Role Play",
            "롤플레잉",
        )
        sudden_questions = self._load_questions_from_file(
            DATA_ROOT / f"{level_prefix}_돌발문제.json",
            "Follow-up",
            "돌발문제",
        )

        return [
            SELF_INTRO_QUESTION,
            *topic_questions,
            *self._pick_roleplay_topic_questions(roleplay_questions, 3),
            *self._pick_sudden_topic_questions(sudden_questions, 2),
        ][:MOCK_TEST_QUESTION_COUNT]

    def _load_grouped_topic_questions(self, level_prefix: str, selected_topics: list[str]) -> list[dict[str, str]]:
        topic_names = self._resolve_mock_topic_groups(level_prefix, selected_topics)
        questions: list[dict[str, str]] = []
        for topic_name in topic_names:
            file_path = DATA_ROOT / f"{level_prefix}_topic" / f"{level_prefix}_topic_{topic_name}.json"
            topic_questions = self._load_questions_from_file(file_path, "Topic", topic_name)
            questions.extend(self._pick_questions(topic_questions, 3))
        return questions

    def _load_topic_questions(self, level_prefix: str, selected_topics: list[str]) -> list[dict[str, str]]:
        questions: list[dict[str, str]] = []
        topic_names = selected_topics or self._available_topic_names(level_prefix)
        for topic_name in topic_names:
            file_path = DATA_ROOT / f"{level_prefix}_topic" / f"{level_prefix}_topic_{topic_name}.json"
            if file_path.exists():
                questions.extend(self._load_questions_from_file(file_path, "Topic", topic_name))

        if questions:
            return questions

        for topic_name in self._available_topic_names(level_prefix):
            questions.extend(
                self._load_questions_from_file(
                    DATA_ROOT / f"{level_prefix}_topic" / f"{level_prefix}_topic_{topic_name}.json",
                    "Topic",
                    topic_name,
                )
            )
        return questions

    @staticmethod
    def _load_questions_from_file(file_path: Path, question_type: str, category: str) -> list[dict[str, str]]:
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question data file not found: {file_path.name}")
        with file_path.open("r", encoding="utf-8-sig") as file:
            items = json.load(file)
        return [
            {
                "questionType": question_type,
                "questionText": str(item.get("text", "")),
                "translation": str(item.get("translation", "")),
                "hint": str(item.get("hint", "")),
                "category": str(item.get("topicTitle") or category),
                "sourceId": str(item.get("id", "")),
                "topicId": str(item.get("topicId", "")),
            }
            for item in items
            if item.get("text")
        ]

    @staticmethod
    def _pick_roleplay_topic_questions(questions: list[dict[str, str]], count: int) -> list[dict[str, str]]:
        return MockTestService._pick_grouped_topic_questions(questions, count)

    @staticmethod
    def _pick_sudden_topic_questions(questions: list[dict[str, str]], count: int) -> list[dict[str, str]]:
        return MockTestService._pick_grouped_topic_questions(questions, count)

    @staticmethod
    def _pick_grouped_topic_questions(questions: list[dict[str, str]], count: int) -> list[dict[str, str]]:
        grouped_questions: dict[str, list[dict[str, str]]] = {}
        for question in questions:
            topic_id = question.get("topicId")
            if not topic_id:
                continue
            grouped_questions.setdefault(topic_id, []).append(question)

        if not grouped_questions:
            return MockTestService._pick_questions(questions, count)

        selected_topic_id = random.choice(list(grouped_questions.keys()))
        selected_questions = grouped_questions[selected_topic_id]
        picked_questions = MockTestService._pick_questions(selected_questions, count)
        return sorted(picked_questions, key=lambda question: int(question.get("sourceId") or 0))

    @staticmethod
    def _pick_questions(questions: list[dict[str, str]], count: int) -> list[dict[str, str]]:
        if len(questions) <= count:
            return questions
        return random.sample(questions, k=count)

    def _resolve_mock_topic_groups(self, level_prefix: str, selected_topics: list[str]) -> list[str]:
        available_topics = self._available_topic_names(level_prefix)
        topic_names = [topic for topic in selected_topics if topic in available_topics]
        for topic in available_topics:
            if len(topic_names) >= 3:
                break
            if topic not in topic_names:
                topic_names.append(topic)
        return topic_names[:3]

    @staticmethod
    def _resolve_level_prefix(difficulty: str) -> str:
        if difficulty == "3-4":
            return "level34"
        if difficulty == "5-6":
            return "level56"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported difficulty.")

    @staticmethod
    def _resolve_selected_topics(payload: MockTestSessionCreateRequest) -> list[str]:
        raw_choices = [
            *payload.selectedLeisure,
            *payload.selectedHobbies,
            *payload.selectedExercises,
            *payload.selectedTravel,
        ]
        topic_names: list[str] = []
        for choice in raw_choices:
            topic_name = TOPIC_NAME_MAP.get(choice)
            if topic_name and topic_name not in topic_names:
                topic_names.append(topic_name)
        return topic_names

    @staticmethod
    def _available_topic_names(level_prefix: str) -> list[str]:
        topic_dir = DATA_ROOT / f"{level_prefix}_topic"
        return [
            path.stem.replace(f"{level_prefix}_topic_", "")
            for path in topic_dir.glob(f"{level_prefix}_topic_*.json")
        ]

    def _get_session(self, session_id: int, user_id: int) -> MockTestSession:
        session = self.db.scalar(
            select(MockTestSession).where(MockTestSession.id == session_id).where(MockTestSession.user_id == user_id)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock test session not found.")
        return session
