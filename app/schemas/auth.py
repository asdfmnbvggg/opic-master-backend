from __future__ import annotations

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=8, max_length=50)
    name: str = Field(min_length=1, max_length=50)
    email: str
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


class FindIdRequest(BaseModel):
    name: str
    email: str


class ResetPasswordRequest(BaseModel):
    username: str
    email: str


class ResetPasswordConfirmRequest(BaseModel):
    token: str
    newPassword: str = Field(min_length=8, max_length=50)


class AuthMessageResponse(BaseModel):
    message: str
    resetLink: str | None = None
