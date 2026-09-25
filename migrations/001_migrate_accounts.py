from __future__ import annotations

from backend.database import db
from backend.secure_core import ensure_all_account_numbers, migrate_user_account_if_needed
from database.indexes import create_indexes

def migrate() -> None:
    create_indexes(db)
    ensure_all_account_numbers()
    users = list(db["users"].find({}, {"username": 1}))
    migrated = 0
    for user in users:
        username = user.get("username")
        if not username:
            continue
        before = db["accounts"].count_documents({"owner_user_id": user["_id"]})
        migrate_user_account_if_needed(username)
        after = db["accounts"].count_documents({"owner_user_id": user["_id"]})
        if after > before:
            migrated += 1
    print(f"Migration completed. New account records: {migrated}")

if __name__ == "__main__":
    migrate()
