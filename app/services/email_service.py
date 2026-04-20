from __future__ import annotations

import smtplib
from email.message import EmailMessage

from fastapi import HTTPException, status

from app.config import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)


class EmailService:
    @staticmethod
    def send_email(*, to_email: str, subject: str, body: str) -> None:
        if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD or not SMTP_FROM_EMAIL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SMTP email settings are not configured.",
            )

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = to_email
        message.set_content(body)

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {exc}",
            ) from exc
