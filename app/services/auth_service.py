from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import PasswordResetToken, User
from app.schemas.auth import (
    AuthMessageResponse,
    FindIdRequest,
    LoginRequest,
    ResetPasswordConfirmRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UsernameCheckResponse,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def signup(self, payload: SignupRequest) -> TokenResponse:
        if self.db.scalar(select(User).where(User.username == payload.username)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")
        if self.db.scalar(select(User).where(User.email == payload.email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")

        birth_date = None
        if payload.birthDate:
            birth_date = datetime.strptime(payload.birthDate, "%Y-%m-%d").date()

        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            name=payload.name,
            email=payload.email,
            birth_date=birth_date,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._build_token_response(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.db.scalar(select(User).where(User.username == payload.username))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

        user.last_login_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return self._build_token_response(user)

    def check_username(self, username: str) -> UsernameCheckResponse:
        exists = self.db.scalar(select(User).where(User.username == username)) is not None
        return UsernameCheckResponse(
            available=not exists,
            message="사용 가능한 아이디입니다." if not exists else "이미 사용 중인 아이디입니다.",
        )

    def find_id(self, payload: FindIdRequest) -> AuthMessageResponse:
        user = self.db.scalar(select(User).where(User.name == payload.name).where(User.email == payload.email))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        masked_username = self._mask_username(user.username)
        return AuthMessageResponse(message=f"가입된 아이디는 {masked_username} 입니다.")

    def request_password_reset(self, payload: ResetPasswordRequest) -> AuthMessageResponse:
        user = self.db.scalar(select(User).where(User.username == payload.username).where(User.email == payload.email))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        self.db.add(reset_token)
        self.db.commit()

        reset_link = f"http://localhost:5173/reset-password?token={token}"
        # TODO(USER): 실제 서비스에서는 여기서 이메일 발송 서비스(예: SES, Resend)를 연결하고 링크를 메일로 보내야 합니다.
        # TODO(USER): 운영 배포 시 reset 링크 도메인을 실제 프론트 도메인으로 변경해야 합니다.
        return AuthMessageResponse(
            message="비밀번호 재설정 링크를 이메일로 발송했습니다.",
            resetLink=reset_link,
        )

    def confirm_password_reset(self, payload: ResetPasswordConfirmRequest) -> AuthMessageResponse:
        reset_token = self.db.scalar(
            select(PasswordResetToken)
            .where(PasswordResetToken.token == payload.token)
            .where(PasswordResetToken.is_used.is_(False))
        )
        if reset_token is None or reset_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset verification failed.")

        user = self.db.scalar(select(User).where(User.id == reset_token.user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        user.password_hash = hash_password(payload.newPassword)
        reset_token.is_used = True
        self.db.commit()
        return AuthMessageResponse(message="비밀번호가 변경되었습니다.")

    @staticmethod
    def _build_token_response(user: User) -> TokenResponse:
        return TokenResponse(
            accessToken=create_access_token(user.id),
            user={
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
            },
        )

    @staticmethod
    def _mask_username(username: str) -> str:
        if len(username) <= 2:
            return username[0] + "*"
        return username[:2] + "*" * max(1, len(username) - 2)
