from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import EVALUATION_AUDIO_DIR, MEDIA_ROOT, MEDIA_URL_PREFIX, PUBLIC_BACKEND_BASE_URL
from app.db.models.evaluation import EvaluationAnswer, EvaluationSession
from app.db.models.saved_content import SavedQuestion, StudyRecord
from app.schemas.evaluation import (
    EvaluationAnswerResponse,
    EvaluationQuestionPayload,
    EvaluationSessionCreateRequest,
    EvaluationSessionResponse,
    SavedAnswerResponse,
)
from app.services.evaluation_ai import build_answer_feedback, build_session_summary
from app.services.evaluation_metrics import compute_answer_metrics
from app.services.stt import guess_file_suffix
from app.services.stt_client import transcribe_with_fallback


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        EVALUATION_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    def create_session(self, user_id: int, payload: EvaluationSessionCreateRequest) -> EvaluationSessionResponse:
        question_payload = [self._question_payload_to_dict(question) for question in payload.questions]
        metadata = dict(payload.metadata)
        metadata["questions"] = question_payload

        session = EvaluationSession(
            user_id=user_id,
            mode=payload.mode,
            status="in_progress",
            title=payload.title,
            difficulty=payload.difficulty,
            total_questions=len(question_payload),
            completed_questions=0,
            metadata_json=json.dumps(metadata),
            overall_strengths_json=json.dumps([]),
            overall_weaknesses_json=json.dumps([]),
            overall_feedback_json=json.dumps({"summary": "Session in progress."}),
            overall_tips_json=json.dumps([]),
            category_scores_json=json.dumps(
                {
                    "grammar": 0,
                    "fluency": 0,
                    "vocabulary": 0,
                    "completion": 0,
                    "relevance": 0,
                    "speed": 0,
                    "engagement": 0,
                }
            ),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self._build_session_response(session, [])

    def submit_answer(
        self,
        *,
        user_id: int,
        session_id: int,
        mode: str,
        question_id: str,
        question_order: int,
        question_text: str,
        question_type: str | None,
        language: str,
        client_duration_seconds: float,
        audio_bytes: bytes | None,
        content_type: str | None,
        client_transcript: str | None = None,
    ) -> EvaluationAnswerResponse:
        session = self._get_session(session_id, user_id)
        if session.mode != mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session mode does not match answer mode.")

        answer = self.db.scalar(
            select(EvaluationAnswer)
            .where(EvaluationAnswer.session_id == session.id)
            .where(EvaluationAnswer.question_id == question_id)
        )
        if answer is None:
            answer = EvaluationAnswer(
                session_id=session.id,
                user_id=user_id,
                mode=mode,
                question_id=question_id,
                question_order=question_order,
                question_type=question_type,
                question_text=question_text,
            )
            self.db.add(answer)

        answer.mode = mode
        answer.question_order = question_order
        answer.question_type = question_type
        answer.question_text = question_text
        answer.audio_duration_seconds = max(0.0, float(client_duration_seconds or 0.0))

        stt_payload: dict[str, Any]
        if audio_bytes:
            audio_path, audio_url = self._persist_audio_file(
                session_id=session.id,
                question_id=question_id,
                audio_bytes=audio_bytes,
                content_type=content_type,
            )
            answer.audio_file_path = audio_path.as_posix()
            answer.audio_url = audio_url
            try:
                stt_payload = transcribe_with_fallback(
                    audio_bytes=audio_bytes,
                    content_type=content_type,
                    language=language,
                    question_id=question_id,
                )
            except HTTPException as stt_exc:
                stt_payload = {
                    "transcript": (client_transcript or "").strip(),
                    "confidence": None,
                    "segments": [],
                    "provider": "client-browser",
                    "stt_error": str(stt_exc.detail),
                }
        else:
            stt_payload = {
                "transcript": (client_transcript or "").strip(),
                "confidence": 0.0,
                "segments": [],
            }

        answer.original_transcript = str(stt_payload.get("transcript") or "").strip()
        answer.transcript_confidence = _safe_float(stt_payload.get("confidence"))
        answer.stt_segments_json = json.dumps(stt_payload.get("segments", []))

        edited_transcript = (answer.edited_transcript or "").strip()
        answer.used_transcript = edited_transcript or answer.original_transcript

        self._apply_metrics_and_feedback(answer)
        self._sync_session_progress(session)

        self.db.commit()
        self.db.refresh(answer)
        self.db.refresh(session)
        return self._build_answer_response(answer)

    def update_transcript(self, *, user_id: int, answer_id: int, transcript: str) -> EvaluationAnswerResponse:
        answer = self._get_answer(answer_id, user_id)
        next_transcript = transcript.strip()
        answer.edited_transcript = next_transcript or None
        answer.used_transcript = next_transcript or answer.original_transcript
        self.db.commit()
        self.db.refresh(answer)
        return self._build_answer_response(answer)

    def re_evaluate_answer(self, *, user_id: int, answer_id: int) -> EvaluationAnswerResponse:
        answer = self._get_answer(answer_id, user_id)
        answer.used_transcript = (answer.edited_transcript or "").strip() or answer.original_transcript
        self._apply_metrics_and_feedback(answer)
        self.db.commit()
        self.db.refresh(answer)
        return self._build_answer_response(answer)

    def complete_session(self, *, user_id: int, session_id: int) -> EvaluationSessionResponse:
        session = self._get_session(session_id, user_id)
        answers = self._get_session_answers(session.id)
        answer_feedback = [self._deserialize_json(answer.feedback_json, {}) for answer in answers]
        overall = build_session_summary(answer_feedback)

        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.overall_strengths_json = json.dumps(overall["strengths"])
        session.overall_weaknesses_json = json.dumps(overall["weaknesses"])
        session.overall_feedback_json = json.dumps(overall["feedback"])
        session.overall_tips_json = json.dumps(overall["tips"])
        session.category_scores_json = json.dumps(overall["categoryScores"])
        session.estimated_grade = overall["estimatedGrade"]
        session.is_gradable = bool(overall["isGradable"])
        self._sync_session_progress(session)

        score = 0
        category_scores = overall["categoryScores"]
        if category_scores:
            score = round(sum(int(value) for value in category_scores.values()) / len(category_scores))

        study_record = self.db.scalar(
            select(StudyRecord)
            .where(StudyRecord.user_id == user_id)
            .where(StudyRecord.record_type == session.mode)
            .where(StudyRecord.source_id == session.id)
        )
        if study_record is None:
            study_record = StudyRecord(
                user_id=user_id,
                record_type=session.mode,
                source_id=session.id,
                grade=session.estimated_grade or "Not enough data",
                score=score,
                duration_seconds=round(sum(answer.audio_duration_seconds for answer in answers)),
            )
            self.db.add(study_record)
        else:
            study_record.grade = session.estimated_grade or "Not enough data"
            study_record.score = score
            study_record.duration_seconds = round(sum(answer.audio_duration_seconds for answer in answers))

        self.db.commit()
        self.db.refresh(session)
        return self._build_session_response(session, answers)

    def get_session_result(self, *, user_id: int, session_id: int) -> EvaluationSessionResponse:
        session = self._get_session(session_id, user_id)
        answers = self._get_session_answers(session.id)
        return self._build_session_response(session, answers)

    def save_answer(self, *, user_id: int, answer_id: int) -> SavedAnswerResponse:
        answer = self._get_answer(answer_id, user_id)
        existing = self.db.scalar(
            select(SavedQuestion)
            .where(SavedQuestion.user_id == user_id)
            .where(SavedQuestion.question_text == answer.question_text)
            .where(SavedQuestion.answer_text == answer.used_transcript)
            .where(SavedQuestion.question_index == answer.question_order)
            .where(SavedQuestion.deleted_at.is_(None))
        )

        if existing is None:
            existing = SavedQuestion(
                user_id=user_id,
                question_text=answer.question_text,
                answer_text=answer.used_transcript,
                category=answer.question_type,
                level=answer.mode,
                question_index=answer.question_order,
            )
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)

        return SavedAnswerResponse(savedId=existing.id, message="Question and answer saved.")

    def _apply_metrics_and_feedback(self, answer: EvaluationAnswer) -> None:
        segments = self._deserialize_json(answer.stt_segments_json, [])
        metrics = compute_answer_metrics(
            question_text=answer.question_text,
            used_transcript=answer.used_transcript,
            audio_duration_seconds=float(answer.audio_duration_seconds or 0.0),
            transcript_confidence=answer.transcript_confidence,
            segments=segments,
        )
        feedback = build_answer_feedback(
            question_text=answer.question_text,
            transcript=answer.used_transcript,
            metrics=metrics,
        )

        answer.word_count = int(metrics["word_count"])
        answer.sentence_count = int(metrics["sentence_count"])
        answer.avg_sentence_length = float(metrics["avg_sentence_length"])
        answer.repetition_rate = float(metrics["repetition_rate"])
        answer.lexical_diversity = float(metrics["lexical_diversity"])
        answer.keyword_similarity = float(metrics["keyword_similarity"])
        answer.speech_duration_seconds = float(metrics["speech_duration_seconds"])
        answer.silence_duration_seconds = float(metrics["silence_duration_seconds"])
        answer.silence_ratio = float(metrics["silence_ratio"])
        answer.pause_count = int(metrics["pause_count"])
        answer.avg_pause_seconds = float(metrics["avg_pause_seconds"])
        answer.speech_rate_wpm = float(metrics["speech_rate_wpm"])
        answer.filler_count = int(metrics["filler_count"])
        answer.filler_ratio = float(metrics["filler_ratio"])
        answer.too_short = bool(metrics["too_short"])
        answer.too_much_silence = bool(metrics["too_much_silence"])
        answer.is_gradable = bool(metrics["is_gradable"])
        answer.feedback_json = json.dumps(feedback)
        answer.estimated_sub_grade = feedback.get("estimatedSubGrade")

    def _sync_session_progress(self, session: EvaluationSession) -> None:
        answers = self._get_session_answers(session.id)
        session.completed_questions = sum(
            1
            for answer in answers
            if (answer.used_transcript or answer.original_transcript or "").strip()
            or answer.audio_file_path
        )
        if session.status != "completed":
            session.status = "in_progress"

    def _get_session(self, session_id: int, user_id: int) -> EvaluationSession:
        session = self.db.scalar(
            select(EvaluationSession)
            .where(EvaluationSession.id == session_id)
            .where(EvaluationSession.user_id == user_id)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation session not found.")
        return session

    def _get_answer(self, answer_id: int, user_id: int) -> EvaluationAnswer:
        answer = self.db.scalar(
            select(EvaluationAnswer)
            .where(EvaluationAnswer.id == answer_id)
            .where(EvaluationAnswer.user_id == user_id)
        )
        if answer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation answer not found.")
        return answer

    def _get_session_answers(self, session_id: int) -> list[EvaluationAnswer]:
        return self.db.scalars(
            select(EvaluationAnswer)
            .where(EvaluationAnswer.session_id == session_id)
            .order_by(EvaluationAnswer.question_order.asc())
        ).all()

    def _persist_audio_file(
        self,
        *,
        session_id: int,
        question_id: str,
        audio_bytes: bytes,
        content_type: str | None,
    ) -> tuple[Path, str]:
        session_dir = EVALUATION_AUDIO_DIR / f"session-{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)

        safe_question_id = re.sub(r"[^A-Za-z0-9_-]+", "-", question_id).strip("-") or "question"
        file_name = f"{safe_question_id}-{uuid.uuid4().hex[:10]}{guess_file_suffix(content_type)}"
        file_path = session_dir / file_name
        file_path.write_bytes(audio_bytes)

        relative_path = file_path.relative_to(MEDIA_ROOT).as_posix()
        audio_url = f"{PUBLIC_BACKEND_BASE_URL}{MEDIA_URL_PREFIX}/{relative_path}"
        return file_path, audio_url

    def _build_session_response(
        self,
        session: EvaluationSession,
        answers: list[EvaluationAnswer],
    ) -> EvaluationSessionResponse:
        metadata = self._deserialize_json(session.metadata_json, {})
        questions = [
            EvaluationQuestionPayload(**question)
            for question in metadata.get("questions", [])
            if isinstance(question, dict)
        ]
        overall = {
            "strengths": self._deserialize_json(session.overall_strengths_json, []),
            "weaknesses": self._deserialize_json(session.overall_weaknesses_json, []),
            "feedback": self._deserialize_json(session.overall_feedback_json, {"summary": "Session in progress."}),
            "tips": self._deserialize_json(session.overall_tips_json, []),
            "categoryScores": self._deserialize_json(
                session.category_scores_json,
                {
                    "grammar": 0,
                    "fluency": 0,
                    "vocabulary": 0,
                    "completion": 0,
                    "relevance": 0,
                    "speed": 0,
                    "engagement": 0,
                },
            ),
            "estimatedGrade": session.estimated_grade,
            "isGradable": session.is_gradable,
        }

        return EvaluationSessionResponse(
            id=session.id,
            mode=session.mode,
            status=session.status,
            title=session.title,
            difficulty=session.difficulty,
            totalQuestions=session.total_questions,
            completedQuestions=session.completed_questions,
            metadata=metadata,
            questions=questions,
            answers=[self._build_answer_response(answer) for answer in answers],
            overall=overall,
            createdAt=session.created_at.isoformat(),
            updatedAt=session.updated_at.isoformat(),
        )

    def _build_answer_response(self, answer: EvaluationAnswer) -> EvaluationAnswerResponse:
        feedback = self._deserialize_json(answer.feedback_json, {})
        metrics = {
            "wordCount": answer.word_count,
            "sentenceCount": answer.sentence_count,
            "avgSentenceLength": round(answer.avg_sentence_length, 2),
            "repetitionRate": round(answer.repetition_rate, 4),
            "lexicalDiversity": round(answer.lexical_diversity, 4),
            "keywordSimilarity": round(answer.keyword_similarity, 4),
            "speechDurationSeconds": round(answer.speech_duration_seconds, 2),
            "silenceDurationSeconds": round(answer.silence_duration_seconds, 2),
            "silenceRatio": round(answer.silence_ratio, 4),
            "pauseCount": answer.pause_count,
            "avgPauseSeconds": round(answer.avg_pause_seconds, 2),
            "speechRateWpm": round(answer.speech_rate_wpm, 2),
            "fillerCount": answer.filler_count,
            "fillerRatio": round(answer.filler_ratio, 4),
            "tooShort": answer.too_short,
            "tooMuchSilence": answer.too_much_silence,
            "isGradable": answer.is_gradable,
        }

        feedback_payload = {
            "strengths": feedback.get("strengths", []),
            "weaknesses": feedback.get("weaknesses", []),
            "scores": feedback.get(
                "scores",
                {
                    "grammar": 0,
                    "fluency": 0,
                    "vocabulary": 0,
                    "completion": 0,
                    "relevance": 0,
                    "speed": 0,
                    "engagement": 0,
                },
            ),
            "feedback": feedback.get(
                "feedback",
                {
                    "grammar": "",
                    "fluency": "",
                    "vocabulary": "",
                    "completion": "",
                    "relevance": "",
                    "speed": "",
                    "sentenceLength": "",
                    "repetition": "",
                    "engagement": "",
                    "answerTime": "",
                    "keywordSimilarity": "",
                },
            ),
            "tips": feedback.get("tips", []),
            "estimatedSubGrade": feedback.get("estimatedSubGrade"),
            "tooShort": feedback.get("tooShort", answer.too_short),
            "tooMuchSilence": feedback.get("tooMuchSilence", answer.too_much_silence),
            "questionRelevance": feedback.get("questionRelevance", ""),
            "sentenceLength": feedback.get("sentenceLength", ""),
            "answerTime": feedback.get("answerTime", ""),
            "repetitionRate": feedback.get("repetitionRate", ""),
            "keywordSimilarity": feedback.get("keywordSimilarity", ""),
        }

        return EvaluationAnswerResponse(
            id=answer.id,
            sessionId=answer.session_id,
            mode=answer.mode,
            questionId=answer.question_id,
            questionOrder=answer.question_order,
            questionType=answer.question_type,
            questionText=answer.question_text,
            audioUrl=answer.audio_url,
            audioDurationSeconds=round(answer.audio_duration_seconds, 2),
            originalTranscript=answer.original_transcript,
            editedTranscript=answer.edited_transcript,
            usedTranscript=answer.used_transcript,
            transcriptConfidence=answer.transcript_confidence,
            metrics=metrics,
            feedback=feedback_payload,
            estimatedSubGrade=answer.estimated_sub_grade,
            createdAt=answer.created_at.isoformat(),
            updatedAt=answer.updated_at.isoformat(),
        )

    @staticmethod
    def _deserialize_json(raw_value: str | None, default: Any) -> Any:
        if not raw_value:
            return default
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return default

    @staticmethod
    def _question_payload_to_dict(question: EvaluationQuestionPayload) -> dict[str, Any]:
        if hasattr(question, "model_dump"):
            return question.model_dump()
        return question.dict()


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
