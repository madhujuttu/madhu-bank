import re
from backend.database import (
    users_collection,
    transactions_collection
)
from config.settings import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    ADMIN_EMAIL,
)
from backend.security import verify_password


def get_admin_email(identifier=None) -> str:
    """Resolve the administrative email address for notifications and OTP delivery."""
    clean_id = str(identifier or "").strip().lower()

    if "@" in clean_id:
        user = users_collection.find_one({
            "email": {"$regex": f"^{re.escape(clean_id)}$", "$options": "i"},
            "role": "admin",
        })
        if user and user.get("email"):
            return str(user["email"]).strip().lower()
        if clean_id == ADMIN_EMAIL.lower():
            return ADMIN_EMAIL.lower()

    if clean_id:
        user = users_collection.find_one({
            "username": clean_id,
            "role": "admin",
        })
        if user and user.get("email"):
            return str(user["email"]).strip().lower()

    admin_user = users_collection.find_one({"role": "admin"})
    if admin_user and admin_user.get("email"):
        return str(admin_user["email"]).strip().lower()

    return ADMIN_EMAIL.lower()


def admin_login(identifier, password):
    """Authenticate an administrator by Email or Username and Password.

    Supports:
    - Configured ADMIN_EMAIL or ADMIN_USERNAME with ADMIN_PASSWORD.
    - Any MongoDB user with role='admin' matching email or username.
    """
    clean_id = str(identifier or "").strip()
    clean_id_lower = clean_id.lower()
    raw_password = str(password or "")

    if not clean_id or not raw_password:
        return False

    # 1. Check against configured static/env admin credentials
    id_matches_config = (
        clean_id_lower == ADMIN_USERNAME.lower()
        or clean_id_lower == ADMIN_EMAIL.lower()
    )
    if id_matches_config and raw_password == ADMIN_PASSWORD:
        return True

    # 2. Check against MongoDB users with role='admin'
    query = {
        "role": "admin",
        "$or": [
            {"username": clean_id},
            {"email": {"$regex": f"^{re.escape(clean_id_lower)}$", "$options": "i"}},
        ],
    }
    user = users_collection.find_one(query)
    if user:
        stored_hash = user.get("password") or user.get("password_hash")
        if stored_hash:
            try:
                if verify_password(raw_password, str(stored_hash)):
                    return True
            except Exception:
                pass
        if stored_hash and str(stored_hash) == raw_password:
            return True

    return False


def get_all_accounts():

    accounts = users_collection.find(
        {},
        {
            "_id": 0,
            "password": 0
        }
    )

    return list(accounts)


def search_accounts(search_text):

    accounts = users_collection.find(
        {
            "$or": [
                {
                    "username": {
                        "$regex": search_text,
                        "$options": "i"
                    }
                },
                {
                    "name": {
                        "$regex": search_text,
                        "$options": "i"
                    }
                }
            ]
        },
        {
            "_id": 0,
            "password": 0
        }
    )

    return list(accounts)


def delete_account(username):
    result = users_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        return False
    transactions_collection.delete_many({"username": username})
    return True


def disable_account(username):

    result = users_collection.update_one(
        {
            "username": username
        },
        {
            "$set": {
                "status": "Disabled"
            }
        }
    )

    if result.modified_count > 0:
        try:
            from backend.alerts import dispatch_system_alert
            dispatch_system_alert(
                alert_type="ACCOUNT_STATUS_CHANGE",
                title=f"Account Frozen: {username}",
                message=f"Customer account '{username}' has been frozen/disabled by Administrator.",
                severity="warning",
                metadata={"username": username, "action": "freeze"},
                send_email=True,
            )
        except Exception:
            pass

    return result.modified_count > 0


def enable_account(username):

    result = users_collection.update_one(
        {
            "username": username
        },
        {
            "$set": {
                "status": "Active"
            }
        }
    )

    return result.modified_count > 0


def get_total_accounts():

    return users_collection.count_documents({})


def get_active_accounts():

    return users_collection.count_documents(
        {
            "status": "Active"
        }
    )


def get_disabled_accounts():

    return users_collection.count_documents(
        {
            "status": "Disabled"
        }
    )


def get_total_bank_balance():

    result = list(
        users_collection.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "total": {
                            "$sum": "$balance"
                        }
                    }
                }
            ]
        )
    )

    if result:
        return result[0]["total"]

    return 0


def get_total_transactions():
    return transactions_collection.count_documents({})

