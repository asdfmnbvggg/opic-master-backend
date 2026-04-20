from __future__ import annotations

import random
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import EmailVerification, PasswordResetToken, User
from app.services.email_service import EmailService
from app.schemas.auth import (
    AuthMessageResponse,
    EmailSendVerificationRequest,
    EmailVerifyRequest,
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
        if not self._is_email_verified(payload.email, "signup"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email verification is required.")
        if not self._is_valid_password(payload.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must include letters, numbers, and special characters.",
            )

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

    def send_email_verification(self, payload: EmailSendVerificationRequest) -> AuthMessageResponse:
        if self.db.scalar(select(User).where(User.email == payload.email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")

        code = f"{random.randint(0, 999999):06d}"
        verification = EmailVerification(
            email=payload.email,
            code=code,
            purpose="signup",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        self.db.add(verification)
        self.db.commit()

        # TODO(USER): 운영 환경에서는 발신 메일 주소와 SMTP 계정을 프로젝트 전용 계정으로 분리하는 것이 좋습니다.
        EmailService.send_email(
            to_email=payload.email,
            subject="[OPIc Master] 이메일 인증 코드",
            body=(
                "안녕하세요.\n\n"
                f"이메일 인증 코드: {code}\n"
                "인증 코드는 10분 동안 유효합니다.\n\n"
                "본인이 요청하지 않았다면 이 메일을 무시해주세요."
            ),
        )
        return AuthMessageResponse(
            message="이메일 인증 코드가 발송되었습니다.",
        )

    def verify_email(self, payload: EmailVerifyRequest) -> AuthMessageResponse:
        verification = self.db.scalar(
            select(EmailVerification)
            .where(EmailVerification.email == payload.email)
            .where(EmailVerification.purpose == "signup")
            .order_by(EmailVerification.created_at.desc())
        )
        if verification is None or verification.code != payload.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code.")
        if verification.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired.")

        verification.is_verified = True
        self.db.commit()
        return AuthMessageResponse(message="이메일 인증이 완료되었습니다.")

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
        # TODO(USER): 운영 배포 시 reset 링크 도메인을 실제 프론트 도메인으로 변경해야 합니다.
        EmailService.send_email(
            to_email=payload.email,
            subject="[OPIc Master] 비밀번호 재설정 링크",
            body=(
                "안녕하세요.\n\n"
                "아래 링크를 눌러 비밀번호를 재설정해주세요.\n"
                f"{reset_link}\n\n"
                "링크는 1시간 동안 유효합니다.\n"
                "본인이 요청하지 않았다면 이 메일을 무시해주세요."
            ),
        )
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
        if not self._is_valid_password(payload.newPassword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must include letters, numbers, and special characters.",
            )

        user = self.db.scalar(select(User).where(User.id == reset_token.user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        user.password_hash = hash_password(payload.newPassword)
        reset_token.is_used = True
        self.db.commit()
        return AuthMessageResponse(message="비밀번호가 변경되었습니다.")

    def _is_email_verified(self, email: str, purpose: str) -> bool:
        verification = self.db.scalar(
            select(EmailVerification)
            .where(EmailVerification.email == email)
            .where(EmailVerification.purpose == purpose)
            .order_by(EmailVerification.created_at.desc())
        )
        return bool(verification and verification.is_verified and verification.expires_at >= datetime.utcnow())

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

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        has_letter = any(char.isalpha() for char in password)
        has_number = any(char.isdigit() for char in password)
        has_special = any(not char.isalnum() for char in password)
        return has_letter and has_number and has_special
