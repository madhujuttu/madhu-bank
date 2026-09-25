from __future__ import annotations
import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
COMMON_PASSWORDS = {
    "password", "password123", "12345678", "123456789", "qwerty",
    "qwerty123", "admin123", "welcome", "letmein", "iloveyou",
    "abc123", "1234567890",
}

def validate_username(username: str) -> str:
    value = (username or "").strip()
    if not USERNAME_RE.fullmatch(value):
        raise ValueError("Username must be 3-32 characters and contain only letters, numbers, dot, underscore, or hyphen.")
    return value

def validate_password(password: str) -> None:
    if not isinstance(password, str):
        raise ValueError("Password must be text.")
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters.")
    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters.")
    if password.lower() in COMMON_PASSWORDS:
        raise ValueError("That password is too common.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain a special character.")

def validate_note(note: str, max_length: int = 120) -> str:
    value = (note or "").strip()
    if len(value) > max_length:
        raise ValueError(f"Note must not exceed {max_length} characters.")
    return value
