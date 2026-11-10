import pytest
from backend.admin import admin_login, get_admin_email
from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL


def test_admin_login_with_username():
    assert admin_login(ADMIN_USERNAME, ADMIN_PASSWORD) is True
    assert admin_login(ADMIN_USERNAME.upper(), ADMIN_PASSWORD) is True


def test_admin_login_with_email():
    assert admin_login(ADMIN_EMAIL, ADMIN_PASSWORD) is True
    assert admin_login(ADMIN_EMAIL.upper(), ADMIN_PASSWORD) is True


def test_admin_login_invalid_password():
    assert admin_login(ADMIN_USERNAME, "wrong_password") is False
    assert admin_login(ADMIN_EMAIL, "wrong_password") is False


def test_admin_login_invalid_identifier():
    assert admin_login("not_an_admin@example.com", ADMIN_PASSWORD) is False
    assert admin_login("unknown_user", ADMIN_PASSWORD) is False
    assert admin_login("", ADMIN_PASSWORD) is False
    assert admin_login(None, ADMIN_PASSWORD) is False


def test_get_admin_email_resolution():
    resolved = get_admin_email(ADMIN_EMAIL)
    assert resolved == ADMIN_EMAIL.lower()

    resolved_username = get_admin_email(ADMIN_USERNAME)
    assert "@" in resolved_username
    assert resolved_username == ADMIN_EMAIL.lower()


def test_deduplicate_accounts_preserves_email():
    from backend.admin import _deduplicate_accounts
    test_data = [
        {"username": "user1", "status": "Active", "email": "customer1@example.com", "balance": 500},
        {"username": "user1", "status": "Pending Verification", "email": "customer1@example.com", "balance": 0},
        {"username": "user2", "status": "Active", "email": "customer2@example.com", "balance": 100},
    ]
    deduped = _deduplicate_accounts(test_data)
    assert len(deduped) == 2
    assert deduped[0]["username"] == "user1"
    assert deduped[0]["email"] == "customer1@example.com"
    assert deduped[0]["status"] == "Active"
    assert deduped[1]["username"] == "user2"
    assert deduped[1]["email"] == "customer2@example.com"


