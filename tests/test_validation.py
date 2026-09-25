import pytest
from utils.validation import validate_password, validate_username
from backend.security_pin import hash_transaction_pin, verify_transaction_pin_hash
from backend.database import users_collection
from backend.users import register_user
from uuid import uuid4

def test_valid_username():
    assert validate_username("madhu_01") == "madhu_01"


def test_transaction_pin_hash_round_trip_and_masking_contract():
    digest = hash_transaction_pin("123456")
    assert isinstance(digest, str)
    assert digest != "123456"
    assert digest == hash_transaction_pin("123456")
    assert verify_transaction_pin_hash("123456", digest) is True
    assert verify_transaction_pin_hash("654321", digest) is False


def test_transaction_pin_bcrypt_backward_compatibility():
    # Legacy bcrypt PIN hashes (such as user madhu's 212121) must verify correctly
    import bcrypt
    bcrypt_hash = bcrypt.hashpw(b"212121", bcrypt.gensalt()).decode("utf-8")
    assert verify_transaction_pin_hash("212121", bcrypt_hash) is True
    assert verify_transaction_pin_hash("123456", bcrypt_hash) is False
    assert verify_transaction_pin_hash("", bcrypt_hash) is False
    assert verify_transaction_pin_hash("212121", "") is False



def test_register_user_returns_false_for_duplicate_email():
    unique_email = f"{uuid4().hex}@example.com"
    unique_username = f"user_{uuid4().hex[:10]}"

    users_collection.delete_many({"username": unique_username})
    users_collection.delete_many({"email": unique_email})

    assert users_collection.insert_one({
        "name": "Initial User",
        "username": unique_username,
        "password": "placeholder",
        "dob": "2000-01-01",
        "account_type": "Savings",
        "balance": 0,
        "status": "Active",
        "role": "user",
        "email": unique_email,
        "email_verified": True,
    }).inserted_id is not None

    duplicate_username = f"user_{uuid4().hex[:10]}"
    assert register_user(
        "New User",
        duplicate_username,
        "Password@123",
        "2000-01-01",
        "Savings",
        email=unique_email,
    ) is False

    users_collection.delete_many({"username": unique_username})
    users_collection.delete_many({"username": duplicate_username})
    users_collection.delete_many({"email": unique_email})


@pytest.mark.parametrize(
    "password",
    [
        "short",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoNumber!!!!",
        "NoSpecial1234",
        "password123",
    ],
)
def test_weak_passwords(password):
    with pytest.raises(ValueError):
        validate_password(password)
