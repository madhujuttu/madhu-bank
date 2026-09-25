"""Password security helpers for the Madhu Bank educational simulation."""

from __future__ import annotations

import bcrypt
import re


MIN_PASSWORD_LENGTH = 8


class PasswordPolicyError(ValueError):
    """Raised when a new password does not satisfy the password policy."""


def validate_password(password: str) -> None:
    """Validate a new password before hashing.

    Existing passwords are still verifiable by ``verify_password``; this policy
    applies to newly created or reset passwords.
    """
    if not isinstance(password, str):
        raise PasswordPolicyError("Password must be text.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
        )

    if not re.search(r"[A-Z]", password):
        raise PasswordPolicyError("Password must contain an uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise PasswordPolicyError("Password must contain a lowercase letter.")

    if not re.search(r"\d", password):
        raise PasswordPolicyError("Password must contain a number.")

    if not re.search(r"[^A-Za-z0-9]", password):
        raise PasswordPolicyError("Password must contain a special character.")


def hash_password(password: str) -> str:
    """Hash a new password using bcrypt."""
    validate_password(password)

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a stored bcrypt hash."""
    if not isinstance(password, str) or not isinstance(hashed_password, str):
        return False

    if not password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def hash_security_answer(answer: str) -> str:
    """Hash a password-recovery security answer without password complexity rules."""
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Security answer cannot be empty.")

    hashed_answer = bcrypt.hashpw(
        answer.strip().lower().encode("utf-8"),
        bcrypt.gensalt(),
    )
    return hashed_answer.decode("utf-8")
