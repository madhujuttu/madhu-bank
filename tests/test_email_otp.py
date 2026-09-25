import re

from backend.email_otp import (
    generate_and_send_otp,
    generate_otp,
    send_otp_email,
    validate_otp,
)


def test_generate_otp_is_numeric_and_expected_length():
    otp = generate_otp()
    assert re.fullmatch(r"\d{6}", otp)
    assert len(otp) == 6


def test_send_otp_email_uses_smtp_and_returns_true(monkeypatch):
    calls = {}

    class DummySMTP:
        def __init__(self, host, port):
            calls["host"] = host
            calls["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, username, password):
            calls["login"] = (username, password)

        def send_message(self, message):
            calls["message_to"] = message["To"]
            calls["message_subject"] = message["Subject"]
            calls["message_body"] = message.get_payload()[0].get_payload()

    monkeypatch.setattr("backend.email_otp.smtplib.SMTP", DummySMTP)

    result = send_otp_email("user@example.com", "123456")

    assert result is True
    assert calls["host"] == "smtp.gmail.com"
    assert calls["port"] == 587
    assert calls["message_to"] == "user@example.com"
    assert "123456" in calls["message_body"]


def test_generate_and_validate_otp_round_trip(monkeypatch):
    calls = {}

    class DummySMTP:
        def __init__(self, host, port):
            calls["host"] = host
            calls["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, username, password):
            calls["login"] = (username, password)

        def send_message(self, message):
            calls["message_to"] = message["To"]
            calls["message_subject"] = message["Subject"]

    monkeypatch.setattr("backend.email_otp.smtplib.SMTP", DummySMTP)

    otp, sent = generate_and_send_otp("user@example.com", expiry_seconds=60)

    assert sent is True
    assert validate_otp("user@example.com", otp) is True
    assert validate_otp("user@example.com", "000000") is False
