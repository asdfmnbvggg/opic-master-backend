from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import PhoneVerification, User
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


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def signup(self, payload: SignupRequest) -> TokenResponse:
        if self.db.scalar(select(User).where(User.username == payload.username)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")

        verified_phone = self._get_latest_verified_code(payload.phone, "signup")
        if verified_phone is None:
            # TODO(USER): 프론트 회원가입 전에 휴대폰 인증을 강제할지, 개발 단계에서는 완화할지 정책 결정이 필요합니다.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone verification is required.")

        birth_date = None
        if payload.birthDate:
            birth_date = datetime.strptime(payload.birthDate, "%Y-%m-%d").date()

        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            name=payload.name,
            phone=payload.phone,
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

    def send_phone_code(self, payload: PhoneSendCodeRequest) -> AuthMessageResponse:
        code = f"{random.randint(0, 999999):06d}"
        verification = PhoneVerification(
            phone=payload.phone,
            code=code,
            purpose=payload.purpose,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=5),
        )
        self.db.add(verification)
        self.db.commit()

        # TODO(USER): 여기서 실제 SMS 발송 업체 API를 연결해야 합니다. 지금은 서버 로그 확인용 안내 메시지만 반환합니다.
        return AuthMessageResponse(message=f"인증번호가 발송되었습니다. 개발용 코드: {code}")

    def verify_phone_code(self, payload: PhoneVerifyCodeRequest) -> AuthMessageResponse:
        verification = self.db.scalar(
            select(PhoneVerification)
            .where(PhoneVerification.phone == payload.phone)
            .where(PhoneVerification.purpose == payload.purpose)
            .order_by(PhoneVerification.created_at.desc())
        )
        if verification is None or verification.code != payload.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code.")
        if verification.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired.")

        verification.is_verified = True
        self.db.commit()
        return AuthMessageResponse(message="인증번호 확인이 완료되었습니다.")

    def find_id(self, payload: FindIdRequest) -> AuthMessageResponse:
        user = self.db.scalar(select(User).where(User.name == payload.name).where(User.phone == payload.phone))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        # TODO(USER): 실제 서비스에서는 전체 아이디를 그대로 노출하지 말고 일부 마스킹하는 정책을 정하세요.
        return AuthMessageResponse(message=f"가입된 아이디는 {user.username} 입니다.")

    def request_password_reset(self, payload: ResetPasswordRequest) -> AuthMessageResponse:
        user = self.db.scalar(select(User).where(User.username == payload.username).where(User.phone == payload.phone))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")
        return self.send_phone_code(PhoneSendCodeRequest(phone=payload.phone, purpose="reset_password"))

    def confirm_password_reset(self, payload: ResetPasswordConfirmRequest) -> AuthMessageResponse:
        verification = self.db.scalar(
            select(PhoneVerification)
            .where(PhoneVerification.phone == payload.phone)
            .where(PhoneVerification.purpose == "reset_password")
            .where(PhoneVerification.code == payload.code)
            .order_by(PhoneVerification.created_at.desc())
        )
        if verification is None or verification.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset verification failed.")

        user = self.db.scalar(select(User).where(User.username == payload.username).where(User.phone == payload.phone))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching user not found.")

        user.password_hash = hash_password(payload.newPassword)
        self.db.commit()
        return AuthMessageResponse(message="비밀번호가 변경되었습니다.")

    def _get_latest_verified_code(self, phone: str, purpose: str) -> PhoneVerification | None:
        verification = self.db.scalar(
            select(PhoneVerification)
            .where(PhoneVerification.phone == phone)
            .where(PhoneVerification.purpose == purpose)
            .order_by(PhoneVerification.created_at.desc())
        )
        if verification is None or not verification.is_verified:
            return None
        return verification

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
