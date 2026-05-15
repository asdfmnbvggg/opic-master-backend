from __future__ import annotations

import json
import logging
import smtplib
from email.message import EmailMessage
from urllib import error, request

from fastapi import HTTPException, status

from app.config import (
    RESEND_API_KEY,
    RESEND_FROM_EMAIL,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(*, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
        if RESEND_API_KEY:
            EmailService._send_via_resend(
                to_email=to_email,
                subject=subject,
                body=body,
                html_body=html_body,
            )
            return

        EmailService._send_via_smtp(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )

    @staticmethod
    def _send_via_resend(*, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
        if not RESEND_FROM_EMAIL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Resend sender email is not configured.",
            )

        payload = {
            "from": RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": body,
        }
        if html_body:
            payload["html"] = html_body

        req = request.Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=20) as response:
                response.read()
            logger.info("Email sent via Resend to %s with subject %s", to_email, subject)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            logger.exception("Resend failed to send email to %s", to_email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email via Resend: {detail or exc.reason}",
            ) from exc
        except Exception as exc:
            logger.exception("Resend failed to send email to %s", to_email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email via Resend: {exc}",
            ) from exc

    @staticmethod
    def _send_via_smtp(*, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
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
        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
            logger.info("Email sent successfully to %s with subject %s", to_email, subject)
        except Exception as exc:
            logger.exception("Failed to send email to %s", to_email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {exc}",
            ) from exc
