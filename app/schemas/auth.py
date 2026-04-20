from __future__ import annotations

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=8, max_length=50)
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=10, max_length=20)
    email: str | None = None
    birthDate: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: dict[str, str | int | None]


class UsernameCheckResponse(BaseModel):
    available: bool
    message: str


class PhoneSendCodeRequest(BaseModel):
    phone: str
    purpose: str = "signup"


class PhoneVerifyCodeRequest(BaseModel):
    phone: str
    code: str = Field(min_length=6, max_length=6)
    purpose: str = "signup"


class FindIdRequest(BaseModel):
    name: str
    phone: str


class ResetPasswordRequest(BaseModel):
    username: str
    phone: str


class ResetPasswordConfirmRequest(BaseModel):
    username: str
    phone: str
    code: str = Field(min_length=6, max_length=6)
    newPassword: str = Field(min_length=8, max_length=50)


class AuthMessageResponse(BaseModel):
    message: str
