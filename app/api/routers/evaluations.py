from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.evaluation import (
    EvaluationAnswerResponse,
    EvaluationSessionCreateRequest,
    EvaluationSessionResponse,
    SavedAnswerResponse,
    TranscriptUpdateRequest,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.post("/sessions", response_model=EvaluationSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: EvaluationSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationSessionResponse:
    return EvaluationService(db).create_session(current_user.id, payload)


@router.post("/answers", response_model=EvaluationAnswerResponse)
async def submit_answer(
    sessionId: int = Form(...),
    mode: str = Form(...),
    questionId: str = Form(...),
    questionOrder: int = Form(...),
    questionText: str = Form(...),
    questionType: str | None = Form(None),
    language: str = Form("en"),
    clientDurationSeconds: float = Form(0),
    clientTranscript: str | None = Form(None),
    audioFile: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationAnswerResponse:
    audio_bytes: bytes | None = None
    content_type: str | None = None
    if audioFile is not None:
        audio_bytes = await audioFile.read()
        content_type = audioFile.content_type

    return EvaluationService(db).submit_answer(
        user_id=current_user.id,
        session_id=sessionId,
        mode=mode,
        question_id=questionId,
        question_order=questionOrder,
        question_text=questionText,
        question_type=questionType,
        language=language,
        client_duration_seconds=clientDurationSeconds,
        audio_bytes=audio_bytes,
        content_type=content_type,
        client_transcript=clientTranscript,
    )


@router.patch("/answers/{answer_id}/transcript", response_model=EvaluationAnswerResponse)
def update_transcript(
    answer_id: int,
    payload: TranscriptUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationAnswerResponse:
    return EvaluationService(db).update_transcript(
        user_id=current_user.id,
        answer_id=answer_id,
        transcript=payload.transcript,
    )


@router.post("/answers/{answer_id}/re-evaluate", response_model=EvaluationAnswerResponse)
def re_evaluate_answer(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationAnswerResponse:
    return EvaluationService(db).re_evaluate_answer(user_id=current_user.id, answer_id=answer_id)


@router.post("/sessions/{session_id}/complete", response_model=EvaluationSessionResponse)
def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationSessionResponse:
    return EvaluationService(db).complete_session(user_id=current_user.id, session_id=session_id)


@router.get("/sessions/{session_id}/result", response_model=EvaluationSessionResponse)
def get_session_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationSessionResponse:
    return EvaluationService(db).get_session_result(user_id=current_user.id, session_id=session_id)


@router.post("/answers/{answer_id}/save", response_model=SavedAnswerResponse)
def save_answer(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedAnswerResponse:
    return EvaluationService(db).save_answer(user_id=current_user.id, answer_id=answer_id)
