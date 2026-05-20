from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage
from html import escape

logger = logging.getLogger(__name__)


def _smtp_config() -> dict[str, str | int | bool | None]:
    return {
        "host": os.getenv("SMTP_HOST"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("SMTP_FROM", os.getenv("SMTP_USER")),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }


def _frontend_base_url() -> str:
    return os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")


def _send_email(*, to_email: str, subject: str, text_body: str, html_body: str) -> None:
    config = _smtp_config()
    if not config["host"] or not config["from_email"]:
        logger.warning("SMTP not configured; skipping email send to %s: %s", to_email, subject)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["from_email"]
    message["To"] = to_email
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(config["host"], config["port"], timeout=15) as smtp:
        smtp.ehlo()
        if config["use_tls"]:
            smtp.starttls()
            smtp.ehlo()
        if config["user"] and config["password"]:
            smtp.login(config["user"], config["password"])
        smtp.send_message(message)


def send_verification_email(*, to_email: str, name: str, token: str) -> None:
    config = _smtp_config()
    verify_link = f"{_frontend_base_url()}/verify-email?token={token}"

    subject = "Verify your Phlow email"
    text_body = (
        f"Hi {name},\n\n"
        f"Welcome to Phlow. Please verify your email by clicking the link below:\n\n"
        f"{verify_link}\n\n"
        f"This link expires in 24 hours. If you did not create this account, ignore this email.\n"
    )
    html_body = (
        f"<p>Hi {name},</p>"
        f"<p>Welcome to Phlow. Please verify your email by clicking the link below:</p>"
        f'<p><a href="{verify_link}">Verify my email</a></p>'
        f"<p>This link expires in 24 hours. If you did not create this account, ignore this email.</p>"
    )

    if not config["host"] or not config["from_email"]:
        logger.warning(
            "SMTP not configured; skipping email send. Verification link for %s: %s",
            to_email,
            verify_link,
        )
        return

    try:
        _send_email(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)
    except Exception:
        logger.exception("Failed to send verification email to %s", to_email)
        raise


def send_portal_upload_notification(
    *,
    to_email: str,
    bookkeeper_name: str,
    client_name: str,
    link_label: str | None,
    file_count: int,
    client_id: int,
) -> None:
    client_url = f"{_frontend_base_url()}/app/clients/{client_id}"
    label_text = f" via {link_label}" if link_label else ""
    subject = f"New Phlow portal upload for {client_name}"
    text_body = (
        f"Hi {bookkeeper_name},\n\n"
        f"{client_name} uploaded {file_count} file{'s' if file_count != 1 else ''}{label_text}.\n\n"
        f"Review the upload here:\n{client_url}\n"
    )
    html_body = (
        f"<p>Hi {escape(bookkeeper_name)},</p>"
        f"<p>{escape(client_name)} uploaded {file_count} file{'s' if file_count != 1 else ''}{escape(label_text)}.</p>"
        f'<p><a href="{client_url}">Open client workspace</a></p>'
    )
    try:
        _send_email(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)
    except Exception:
        logger.exception("Failed to send portal upload notification to %s", to_email)


def send_portal_comment_notification(
    *,
    to_email: str,
    bookkeeper_name: str,
    client_name: str,
    receipt_name: str,
    commenter_name: str,
    comment_body: str,
    client_id: int,
) -> None:
    client_url = f"{_frontend_base_url()}/app/clients/{client_id}"
    excerpt = comment_body.strip()
    if len(excerpt) > 180:
        excerpt = f"{excerpt[:177]}..."
    subject = f"New Phlow portal comment for {client_name}"
    text_body = (
        f"Hi {bookkeeper_name},\n\n"
        f"{commenter_name} commented on {receipt_name} for {client_name}:\n\n"
        f"{excerpt}\n\n"
        f"Reply here:\n{client_url}\n"
    )
    html_body = (
        f"<p>Hi {escape(bookkeeper_name)},</p>"
        f"<p>{escape(commenter_name)} commented on {escape(receipt_name)} for {escape(client_name)}:</p>"
        f"<blockquote>{escape(excerpt)}</blockquote>"
        f'<p><a href="{client_url}">Open client workspace</a></p>'
    )
    try:
        _send_email(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)
    except Exception:
        logger.exception("Failed to send portal comment notification to %s", to_email)
