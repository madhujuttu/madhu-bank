"""Transfer services for the Madhu Bank educational simulation.

This implementation is compatible with a normal local MongoDB standalone
server (the common Compass/local Community Server setup). It does not require
MongoDB replica-set transaction support. Balance changes are protected with
conditional updates and are rolled back if any later transfer step fails.
"""

from datetime import datetime
from uuid import uuid4

from backend.database import db, users_collection

transactions_collection = db["transactions"]

try:
    transactions_collection.create_index("transaction_id")
    transactions_collection.create_index("account_number")
except Exception:
    pass


def _as_numeric_account_number(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _find_user_by_account_number(account_number):
    numeric_number = _as_numeric_account_number(account_number)
    if numeric_number is None:
        return None
    return users_collection.find_one({"account_number": numeric_number})


def _rollback_sender(sender_number, amount):
    try:
        users_collection.update_one(
            {"account_number": sender_number},
            {"$inc": {"balance": amount}},
        )
        return True
    except Exception:
        return False


def _rollback_receiver(receiver_number, amount):
    try:
        users_collection.update_one(
            {"account_number": receiver_number, "balance": {"$gte": amount}},
            {"$inc": {"balance": -amount}},
        )
        return True
    except Exception:
        return False


def transfer_money(sender_account_number, receiver_account_number, amount, note=""):
    """Transfer money between two Account Numbers.

    The function intentionally avoids MongoDB sessions/transactions so it works
    with a local standalone MongoDB server. It performs conditional balance
    updates and compensating rollbacks when transaction recording fails.
    """
    sender_number = _as_numeric_account_number(sender_account_number)
    receiver_number = _as_numeric_account_number(receiver_account_number)

    if sender_number is None or receiver_number is None:
        return {"ok": False, "message": "Account Numbers must contain numbers only."}

    if sender_number == receiver_number:
        return {"ok": False, "message": "You cannot transfer money to yourself."}

    try:
        transfer_amount = float(amount)
    except (TypeError, ValueError):
        return {"ok": False, "message": "Enter a valid amount."}

    if transfer_amount <= 0:
        return {"ok": False, "message": "Transfer amount must be greater than 0."}

    sender = _find_user_by_account_number(sender_number)
    receiver = _find_user_by_account_number(receiver_number)

    if not sender:
        return {"ok": False, "message": "Sender Account Number was not found."}
    if not receiver:
        return {"ok": False, "message": "Receiver Account Number was not found."}

    if sender.get("status", "Active") != "Active":
        return {"ok": False, "message": "Your account is not active."}
    if receiver.get("status", "Active") != "Active":
        return {"ok": False, "message": "The receiver account is not active."}

    # Step 1: debit sender only when sufficient funds are available.
    updated_sender = users_collection.find_one_and_update(
        {
            "account_number": sender_number,
            "status": "Active",
            "balance": {"$gte": transfer_amount},
        },
        {"$inc": {"balance": -transfer_amount}},
        return_document=True,
    )

    if not updated_sender:
        return {"ok": False, "message": "Insufficient balance for this transfer."}

    receiver_credited = False

    try:
        # Step 2: credit the receiver.
        updated_receiver = users_collection.find_one_and_update(
            {
                "account_number": receiver_number,
                "status": "Active",
            },
            {"$inc": {"balance": transfer_amount}},
            return_document=True,
        )

        if not updated_receiver:
            _rollback_sender(sender_number, transfer_amount)
            return {
                "ok": False,
                "message": "Receiver account could not be credited. No money was transferred.",
            }

        receiver_credited = True

        transfer_id = f"TX-{uuid4().hex[:12].upper()}"
        # Store the actual local clock time of the machine running the app.
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

        sender_username = sender.get("username", "")
        receiver_username = receiver.get("username", "")
        clean_note = str(note or "").strip()

        sender_name = (
            sender.get("name")
            or f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip()
            or sender_username
        )
        receiver_name = (
            receiver.get("name")
            or f"{receiver.get('first_name', '')} {receiver.get('last_name', '')}".strip()
            or receiver_username
        )

        base = {
            "transaction_id": transfer_id,
            "type": "Transfer",
            "amount": transfer_amount,
            "status": "Completed",
            "date": timestamp,
            "transfer_id": transfer_id,
            "note": clean_note,
        }

        sender_transaction = {
            **base,
            "account_number": sender_number,
            "username": sender_username,
            "user_name": sender_name,
            "direction": "Out",
            "counterparty_account_number": receiver_number,
            "counterparty_username": receiver_username,
            "counterparty_name": receiver_name,
            "description": f"Transfer to {receiver_name} (Account Number {receiver_number})",
        }

        receiver_transaction = {
            **base,
            "transaction_id": f"{transfer_id}-IN",
            "account_number": receiver_number,
            "username": receiver_username,
            "user_name": receiver_name,
            "direction": "In",
            "counterparty_account_number": sender_number,
            "counterparty_username": sender_username,
            "counterparty_name": sender_name,
            "description": f"Transfer from {sender_name} (Account Number {sender_number})",
            "notification_seen": False,
        }

        # Step 3: record both sides. If recording fails, compensate both
        # balance updates so the transfer is not left partially completed.
        transactions_collection.insert_many(
            [sender_transaction, receiver_transaction],
            ordered=True,
        )

        return {
            "ok": True,
            "message": "Transfer completed successfully.",
            "transfer_id": transfer_id,
            "sender_balance": float(updated_sender.get("balance", 0)),
            "receiver_balance": float(updated_receiver.get("balance", 0)),
        }

    except Exception as exc:
        # Roll back the receiver first, then the sender, when possible.
        if receiver_credited:
            _rollback_receiver(receiver_number, transfer_amount)
        _rollback_sender(sender_number, transfer_amount)

        return {
            "ok": False,
            "message": f"Transfer could not be completed. No money was transferred. Details: {exc}",
        }
