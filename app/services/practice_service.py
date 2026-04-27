from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.practice import PracticeAnswer, PracticeFeedback, PracticeQuestionSet, PracticeSession
from app.db.models.saved_content import StudyRecord
from app.schemas.practice import (
    PracticeEvaluationRequest,
    PracticeQuestionItem,
    PracticeQuestionSetCreateRequest,
    PracticeQuestionSetResponse,
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
)

DATA_ROOT = Path(__file__).resolve().parents[3] / "opic-master-data"
QUESTION_COUNT = 3
TOPIC_NAME_MAP = {
    "performance": "공연",
    "공연": "공연",
    "domestic_travel": "국내여행",
    "국내여행": "국내여행",
    "국내 여행": "국내여행",
    "cafe": "카페",
    "카페": "카페",
    "exercise": "운동",
    "운동": "운동",
    "home": "집",
    "집": "집",
    "cooking": "요리",
    "요리": "요리",
    "camping": "캠핑",
    "캠핑": "캠핑",
    "jogging_walking": "조깅산책",
    "조깅산책": "조깅산책",
    "조깅/산책": "조깅산책",
    "조깅/걷기": "조깅산책",
    "housing": "사는지역",
    "사는지역": "사는지역",
    "주거": "사는지역",
    "abroad": "해외여행",
    "해외여행": "해외여행",
    "해외 여행": "해외여행",
    "holiday": "휴일",
    "휴일": "휴일",
    "휴일/연휴": "휴일",
    "neighbor": "이웃",
    "이웃": "이웃",
    "drinking_bar": "술집",
    "술집": "술집",
    "술집/회식": "술집",
    "music": "음악",
    "음악": "음악",
    "game": "게임",
    "게임": "게임",
    "beach": "해변",
    "해변": "해변",
    "바다": "해변",
    "park": "공원",
    "공원": "공원",
    "mountain": "산",
    "산": "산",
    "shopping": "쇼핑",
    "쇼핑": "쇼핑",
    "movie": "영화",
    "영화": "영화",
    "job": "구직",
    "구직": "구직",
    "직장": "구직",
    "sns": "SNS",
    "SNS": "SNS",
}


class PracticeService:
    def __init__(self, db: Session):
        self.db = db

    def create_question_set(self, user_id: int, payload: PracticeQuestionSetCreateRequest) -> PracticeQuestionSetResponse:
        questions = self._load_questions_by_ids(
            difficulty=payload.difficulty,
            selected_type=payload.selectedType,
            selected_topics=payload.selectedTopics,
        )
        question_set = PracticeQuestionSet(
            user_id=user_id,
            difficulty=payload.difficulty,
            question_type=payload.selectedType,
            selected_topics=json.dumps(payload.selectedTopics, ensure_ascii=False),
            question_ids=json.dumps([question.id for question in questions], ensure_ascii=False),
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

        questions = self._load_questions_by_ids(
            difficulty=question_set.difficulty,
            selected_type=question_set.question_type,
            selected_topics=json.loads(question_set.selected_topics),
            question_ids=json.loads(question_set.question_ids),
        )
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
            "?듭떖 臾몄옣??癒쇱? 留먰븯?ㅻ뒗 ?먮쫫??蹂댁엯?덈떎.",
            "二쇱젣? 愿?⑤맂 湲곕낯 ?댄쐶 ?ъ슜? ?덉젙?곸엯?덈떎.",
            "?듬? 湲몄씠媛 ?덈Т 吏㏃?留??딅떎硫??꾨떖?μ? 異⑸텇?⑸땲??",
        ]
        improvements = [
            "援ъ껜?곸씤 ?덉떆瑜?1媛쒖뵫留???異붽??대낫?몄슂.",
            "?듬? 泥?臾몄옣????吏곸젒?곸쑝濡??쒖옉?대낫?몄슂.",
            "because, for example 媛숈? ?곌껐 ?쒗쁽???섎젮蹂댁꽭??",
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

    def _load_questions_by_ids(
        self,
        difficulty: str,
        selected_type: str,
        selected_topics: list[str],
        question_ids: list[str] | None = None,
    ) -> list[PracticeQuestionItem]:
        questions = self._load_questions_from_source(difficulty, selected_type, selected_topics)
        if question_ids is None:
            return self._pick_random_questions(questions)

        question_map = {question.id: question for question in questions}
        ordered_questions = [question_map[question_id] for question_id in question_ids if question_id in question_map]
        if len(ordered_questions) != len(question_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some practice questions could not be loaded.")
        return ordered_questions

    def _load_questions_from_source(
        self,
        difficulty: str,
        selected_type: str,
        selected_topics: list[str],
    ) -> list[PracticeQuestionItem]:
        level_prefix = self._resolve_level_prefix(difficulty)

        if selected_type == "topics":
            if not selected_topics:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A topic must be selected.")
            topic_name = self._normalize_topic_name(selected_topics[0])
            file_path = DATA_ROOT / f"{level_prefix}_topic" / f"{level_prefix}_topic_{topic_name}.json"
            category = topic_name
        elif selected_type == "random":
            file_path = DATA_ROOT / f"{level_prefix}_돌발문제.json"
            category = "돌발문제"
        elif selected_type == "roleplaying":
            file_path = DATA_ROOT / f"{level_prefix}_롤플레잉.json"
            category = "롤플레잉"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported practice type.")

        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question data file not found: {file_path.name}")

        # Some source files were saved with a UTF-8 BOM, so accept both plain UTF-8 and UTF-8-SIG.
        with file_path.open("r", encoding="utf-8-sig") as file:
            raw_items = json.load(file)

        return [
            PracticeQuestionItem(
                id=f"{level_prefix}:{selected_type}:{category}:{item['id']}",
                category=self._resolve_question_category(selected_type, category, item),
                text=item["text"],
                translation=item.get("translation", ""),
                hint=item.get("hint", ""),
            )
            for item in raw_items
        ]

    @staticmethod
    def _pick_random_questions(questions: list[PracticeQuestionItem]) -> list[PracticeQuestionItem]:
        if not questions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No practice questions available.")
        sample_size = min(QUESTION_COUNT, len(questions))
        return random.sample(questions, k=sample_size)

    @staticmethod
    def _resolve_level_prefix(difficulty: str) -> str:
        if difficulty == "3-4":
            return "level34"
        if difficulty == "5-6":
            return "level56"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported difficulty.")

    @staticmethod
    def _resolve_question_category(selected_type: str, fallback_category: str, item: dict[str, object]) -> str:
        if selected_type == "topics":
            return fallback_category
        topic_title = item.get("topicTitle")
        if isinstance(topic_title, str) and topic_title.strip():
            return topic_title
        return fallback_category

    @staticmethod
    def _normalize_topic_name(topic: str) -> str:
        normalized = topic.strip()
        mapped = TOPIC_NAME_MAP.get(normalized)
        if mapped:
            return mapped

        mapped = TOPIC_NAME_MAP.get(normalized.lower())
        if mapped:
            return mapped

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported topic: {topic}")

    @staticmethod
    def _build_question_set_response(
        question_set: PracticeQuestionSet,
        questions: list[PracticeQuestionItem],
    ) -> PracticeQuestionSetResponse:
        return PracticeQuestionSetResponse(
            questionSetId=question_set.id,
            difficulty=question_set.difficulty,
            selectedType=question_set.question_type,
            selectedTopics=json.loads(question_set.selected_topics),
            questions=questions,
        )

    @staticmethod
    def _build_feedback(answers: list) -> list[dict[str, object]]:
        feedback_items: list[dict[str, object]] = []
        for index, answer in enumerate(answers, start=1):
            transcript = answer.transcript.strip()
            word_count = len(transcript.split())
            # TODO(USER): ?ㅼ젣 梨꾩젏 紐⑤뜽??遺숈씪 ?뚮뒗 ??洹쒖튃 湲곕컲 ?쇰뱶諛깆쓣 LLM/?됯? ?붿쭊 ?묐떟?쇰줈 援먯껜?섏꽭??
            feedback_items.append(
                {
                    "questionIndex": index,
                    "question": f"Question {index}",
                    "yourAnswer": transcript,
                    "feedbackPoints": [
                        {
                            "label": "Summary",
                            "text": "?듬? 湲몄씠媛 ?곸젅?⑸땲??" if word_count >= 20 else "議곌툑 ??湲멸쾶 ?듯빐蹂대㈃ 醫뗭뒿?덈떎.",
                        },
                        {
                            "label": "Grammar",
                            "text": "湲곕낯 臾몄옣 援ъ“???좎??섍퀬 ?덉뒿?덈떎.",
                        },
                        {
                            "label": "Vocabulary",
                            "text": "諛섎났 ?⑥뼱瑜?以꾩씠怨??좎궗 ?쒗쁽??異붽??대낫?몄슂.",
                        },
                        {
                            "label": "Content",
                            "text": "?댁쑀? ?덉떆瑜??④퍡 留먰븯硫????ㅻ뱷???덉뼱吏묐땲??",
                        },
                    ],
                }
            )
        return feedback_items
