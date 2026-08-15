"""Standalone email + Jinja2 rendering helpers (no Flask dependency).

Background tasks previously depended on ``flask_mail.Message`` and
``flask.render_template``, which in turn require a Flask application object
and an active application context. This module provides a small, framework-free
replacement so Celery workers no longer need Flask at all.

The ``Message`` class mirrors the tiny subset of the Flask-Mail API the tasks
use: ``subject``, ``recipients``, ``sender``, ``html`` and ``attach()``.
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

from server.config.settings import get_settings

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_Attachment = Tuple[Optional[str], Optional[str], Optional[bytes], Optional[str]]


class Message:
    """Minimal Flask-Mail-compatible message object."""

    def __init__(
        self,
        subject: str = "",
        recipients: Optional[List[str]] = None,
        body: Optional[str] = None,
        html: Optional[str] = None,
        sender: Optional[str] = None,
    ):
        self.subject = subject
        self.recipients: List[str] = list(recipients) if recipients else []
        self.body = body
        self.html = html
        self.sender = sender
        self._attachments: List[_Attachment] = []

    def attach(
        self,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        data: Optional[bytes] = None,
        disposition: Optional[str] = None,
    ) -> None:
        self._attachments.append((filename, content_type, data, disposition))

    def _as_email(self) -> EmailMessage:
        msg = EmailMessage()
        if self.subject:
            msg["Subject"] = self.subject
        if self.sender:
            msg["From"] = self.sender
        if self.recipients:
            msg["To"] = ", ".join(self.recipients)

        if self.html is not None:
            if self.body is not None:
                msg.set_content(self.body)
                msg.add_alternative(self.html, subtype="html")
            else:
                msg.set_content(self.html, subtype="html")
        elif self.body is not None:
            msg.set_content(self.body)
        else:
            msg.set_content("")

        for filename, content_type, data, disposition in self._attachments:
            maintype, _, subtype = (content_type or "application/octet-stream").partition(
                "/"
            )
            msg.add_attachment(
                data or b"",
                maintype=maintype or "application",
                subtype=subtype or "octet-stream",
                filename=filename,
                disposition=disposition or "attachment",
            )

        return msg

    def __eq__(self, other) -> bool:
        if not isinstance(other, Message):
            return NotImplemented
        return (
            self.subject == other.subject
            and self.recipients == other.recipients
            and self.body == other.body
            and self.html == other.html
            and self.sender == other.sender
        )

    def __repr__(self) -> str:
        return (
            f"<Message subject={self.subject!r} recipients={self.recipients!r} "
            f"sender={self.sender!r}>"
        )


def send(msg: Message) -> None:
    """Deliver ``msg`` via SMTP using the configured mail settings."""
    settings = get_settings()

    if msg.sender is None:
        msg.sender = settings.default_mail_sender or os.environ.get(
            "DEFAULT_MAIL_SENDER"
        )

    host = settings.mail_server
    if not host:
        # No mail server configured (tests, local dev without SMTP): no-op.
        return

    port = int(settings.mail_port or 25)
    with smtplib.SMTP(host, port) as server:
        if settings.mail_use_tls:
            server.starttls()
        if settings.mail_username:
            server.login(settings.mail_username, settings.mail_password)
        server.send_message(msg._as_email())


def render_template(template_name: str, **kwargs) -> str:
    """Render a Jinja2 template from ``server/templates`` (Flask-free)."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env.get_template(template_name).render(**kwargs)
