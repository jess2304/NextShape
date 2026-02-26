import ssl

import pytest
from api import utils


class DummySMTP:
    last_instance = None

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.starttls_context = None
        self.login_args = None
        self.sent_args = None
        DummySMTP.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        self.starttls_context = context

    def login(self, user, password):
        self.login_args = (user, password)

    def sendmail(self, from_email, recipients, message):
        self.sent_args = (from_email, recipients, message)


@pytest.mark.django_db
def test_send_html_email_uses_verified_tls_context(monkeypatch, settings):
    settings.ENV = "local"
    settings.EMAIL_HOST = "smtp.example.com"
    settings.EMAIL_PORT = 587
    settings.EMAIL_USE_TLS = True
    settings.EMAIL_USE_SSL = False
    settings.EMAIL_TIMEOUT = 12
    settings.EMAIL_HOST_USER = "mailer@example.com"
    settings.EMAIL_HOST_PASSWORD = "secret"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"

    monkeypatch.setattr(utils.smtplib, "SMTP", DummySMTP)

    utils.send_html_email(
        subject="Sujet été",
        to_email="user@example.com",
        html_content="<p>Bonjour été</p>",
    )

    smtp = DummySMTP.last_instance
    assert smtp is not None
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 587
    assert smtp.timeout == 12
    assert smtp.starttls_context is not None
    assert smtp.starttls_context.verify_mode == ssl.CERT_REQUIRED
    assert smtp.starttls_context.check_hostname is True
    assert smtp.login_args == ("mailer@example.com", "secret")
    assert smtp.sent_args is not None
    assert 'charset="utf-8"' in smtp.sent_args[2].lower()


@pytest.mark.django_db
def test_send_html_email_skips_in_test_runtime(monkeypatch, settings):
    settings.ENV = "test"

    def should_not_connect(*args, **kwargs):
        raise AssertionError("SMTP should not be called during tests.")

    monkeypatch.setattr(utils.smtplib, "SMTP", should_not_connect)

    utils.send_html_email(
        subject="Sujet",
        to_email="user@example.com",
        html_content="<p>Bonjour</p>",
    )


@pytest.mark.django_db
def test_send_html_email_raises_if_email_host_missing(settings):
    settings.ENV = "local"
    settings.EMAIL_HOST = ""
    settings.EMAIL_PORT = 587
    settings.EMAIL_USE_TLS = True
    settings.EMAIL_USE_SSL = False
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"

    with pytest.raises(ValueError, match="EMAIL_HOST is not configured"):
        utils.send_html_email(
            subject="Sujet",
            to_email="user@example.com",
            html_content="<p>Bonjour</p>",
        )


def test_send_verification_email_uses_clean_french_content(monkeypatch):
    captured = {}

    def fake_send_html_email(subject, to_email, html_content, reply_to=None):
        captured["subject"] = subject
        captured["to_email"] = to_email
        captured["html_content"] = html_content
        captured["reply_to"] = reply_to

    monkeypatch.setattr(utils, "send_html_email", fake_send_html_email)

    utils.send_verification_email("user@example.com", "123456")

    payload = captured["subject"] + captured["html_content"]
    assert "Vérification" in captured["subject"]
    assert "vérifier" in captured["html_content"]
    assert "L'équipe NextShape" in captured["html_content"]
    assert "Ã" not in payload


def test_send_contact_email_uses_clean_french_content(monkeypatch, settings):
    captured = {}

    def fake_send_html_email(subject, to_email, html_content, reply_to=None):
        captured["subject"] = subject
        captured["to_email"] = to_email
        captured["html_content"] = html_content
        captured["reply_to"] = reply_to

    monkeypatch.setattr(utils, "send_html_email", fake_send_html_email)
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"

    utils.send_contact_email(
        {
            "name": "Élise",
            "email": "elise@example.com",
            "message": "Bonjour, j'ai une question.",
        }
    )

    payload = captured["subject"] + captured["html_content"]
    assert "Vous avez reçu un nouveau message" in captured["html_content"]
    assert captured["reply_to"] == "elise@example.com"
    assert "Ã" not in payload
