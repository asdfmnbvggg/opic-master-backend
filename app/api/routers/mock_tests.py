from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.mock_test import (
    MockTestAnswerUpsertRequest,
    MockTestResultResponse,
    MockTestSessionCreateRequest,
    MockTestSessionResponse,
)
from app.services.mock_test_service import MockTestService

router = APIRouter(prefix="/api/mock-tests", tags=["mock-tests"])


@router.post("/sessions", response_model=MockTestSessionResponse, status_code=status.HTTP_201_CREATED)
def create_mock_test_session(
    payload: MockTestSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockTestSessionResponse:
    return MockTestService(db).create_session(current_user.id, payload)


@router.get("/sessions/{session_id}", response_model=MockTestSessionResponse)
def get_mock_test_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockTestSessionResponse:
    return MockTestService(db).get_session(session_id, current_user.id)


@router.post("/sessions/{session_id}/answers", response_model=MockTestSessionResponse)
def upsert_mock_test_answers(
    session_id: int,
    payload: MockTestAnswerUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockTestSessionResponse:
    return MockTestService(db).save_answers(session_id, current_user.id, payload)


@router.post("/sessions/{session_id}/finish", response_model=MockTestResultResponse)
def finish_mock_test_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockTestResultResponse:
    return MockTestService(db).finish_session(session_id, current_user.id)


@router.get("/sessions/{session_id}/result", response_model=MockTestResultResponse)
def get_mock_test_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockTestResultResponse:
    return MockTestService(db).get_result(session_id, current_user.id)
