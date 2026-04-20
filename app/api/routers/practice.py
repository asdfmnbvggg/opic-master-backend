from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.practice import (
    PracticeEvaluationRequest,
    PracticeQuestionSetCreateRequest,
    PracticeQuestionSetResponse,
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
)
from app.services.practice_service import PracticeService

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.post("/question-sets", response_model=PracticeQuestionSetResponse, status_code=status.HTTP_201_CREATED)
def create_question_set(
    payload: PracticeQuestionSetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeQuestionSetResponse:
    return PracticeService(db).create_question_set(current_user.id, payload)


@router.get("/question-sets/{question_set_id}", response_model=PracticeQuestionSetResponse)
def get_question_set(
    question_set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeQuestionSetResponse:
    return PracticeService(db).get_question_set(question_set_id, current_user.id)


@router.post("/sessions", response_model=PracticeSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: PracticeSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSessionResponse:
    return PracticeService(db).create_session(current_user.id, payload)


@router.post("/sessions/{session_id}/evaluate", response_model=PracticeSessionResponse)
def evaluate_session(
    session_id: int,
    payload: PracticeEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSessionResponse:
    return PracticeService(db).evaluate_session(session_id, current_user.id, payload)


@router.get("/sessions/{session_id}/result", response_model=PracticeSessionResponse)
def get_session_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSessionResponse:
    return PracticeService(db).get_session_result(session_id, current_user.id)
