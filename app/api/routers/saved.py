from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.saved import (
    SavedPhraseCreateRequest,
    SavedPhraseListResponse,
    SavedQuestionCreateRequest,
    SavedQuestionListResponse,
    SavedWordCreateRequest,
    SavedWordListResponse,
)
from app.services.saved_service import SavedService

router = APIRouter(prefix="/api/saved", tags=["saved"])


@router.get("/questions", response_model=SavedQuestionListResponse)
def get_saved_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedQuestionListResponse:
    return SavedService(db).get_saved_questions(current_user.id)


@router.post("/questions", response_model=SavedQuestionListResponse, status_code=status.HTTP_201_CREATED)
def create_saved_question(
    payload: SavedQuestionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedQuestionListResponse:
    return SavedService(db).save_question(current_user.id, payload)


@router.delete("/questions/{saved_id}", response_model=SavedQuestionListResponse)
def delete_saved_question(
    saved_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedQuestionListResponse:
    return SavedService(db).delete_question(current_user.id, saved_id)


@router.post("/questions/{saved_id}/restore", response_model=SavedQuestionListResponse)
def restore_saved_question(
    saved_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedQuestionListResponse:
    return SavedService(db).restore_question(current_user.id, saved_id)


@router.get("/phrases", response_model=SavedPhraseListResponse)
def get_saved_phrases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedPhraseListResponse:
    return SavedService(db).get_saved_phrases(current_user.id)


@router.post("/phrases", response_model=SavedPhraseListResponse, status_code=status.HTTP_201_CREATED)
def create_saved_phrase(
    payload: SavedPhraseCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedPhraseListResponse:
    return SavedService(db).save_phrase(current_user.id, payload)


@router.get("/words", response_model=SavedWordListResponse)
def get_saved_words(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedWordListResponse:
    return SavedService(db).get_saved_words(current_user.id)


@router.post("/words", response_model=SavedWordListResponse, status_code=status.HTTP_201_CREATED)
def create_saved_word(
    payload: SavedWordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedWordListResponse:
    return SavedService(db).save_word(current_user.id, payload)
