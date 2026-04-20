from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.auth import (
    AuthMessageResponse,
    FindIdRequest,
    LoginRequest,
    PhoneSendCodeRequest,
    PhoneVerifyCodeRequest,
    ResetPasswordConfirmRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UsernameCheckResponse,
)
from app.schemas.user import UserProfileResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService(db).signup(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService(db).login(payload)


@router.post("/logout", response_model=AuthMessageResponse)
def logout(_: User = Depends(get_current_user)) -> AuthMessageResponse:
    return AuthMessageResponse(message="Logged out successfully.")


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


@router.get("/check-username", response_model=UsernameCheckResponse)
def check_username(
    username: str = Query(..., min_length=6, max_length=20),
    db: Session = Depends(get_db),
) -> UsernameCheckResponse:
    return AuthService(db).check_username(username)


@router.post("/phone/send-code", response_model=AuthMessageResponse)
def send_phone_code(payload: PhoneSendCodeRequest, db: Session = Depends(get_db)) -> AuthMessageResponse:
    return AuthService(db).send_phone_code(payload)


@router.post("/phone/verify-code", response_model=AuthMessageResponse)
def verify_phone_code(payload: PhoneVerifyCodeRequest, db: Session = Depends(get_db)) -> AuthMessageResponse:
    return AuthService(db).verify_phone_code(payload)


@router.post("/find-id", response_model=AuthMessageResponse)
def find_id(payload: FindIdRequest, db: Session = Depends(get_db)) -> AuthMessageResponse:
    return AuthService(db).find_id(payload)


@router.post("/reset-password/request", response_model=AuthMessageResponse)
def request_password_reset(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> AuthMessageResponse:
    return AuthService(db).request_password_reset(payload)


@router.post("/reset-password/confirm", response_model=AuthMessageResponse)
def confirm_password_reset(
    payload: ResetPasswordConfirmRequest,
    db: Session = Depends(get_db),
) -> AuthMessageResponse:
    return AuthService(db).confirm_password_reset(payload)
