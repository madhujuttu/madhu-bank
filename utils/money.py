from __future__ import annotations
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CURRENCY = "INR"
MINOR_UNIT = Decimal("0.01")

class MoneyError(ValueError):
    """Raised when a monetary value is invalid."""

def to_decimal(value: object) -> Decimal:
    if isinstance(value, bool):
        raise MoneyError("Boolean is not a monetary value.")
    try:
        amount = Decimal(str(value)).quantize(MINOR_UNIT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise MoneyError("Invalid monetary amount.") from exc
    if not amount.is_finite():
        raise MoneyError("Monetary amount must be finite.")
    return amount

def require_positive(value: object) -> Decimal:
    amount = to_decimal(value)
    if amount <= 0:
        raise MoneyError("Amount must be greater than zero.")
    return amount

def to_minor_units(value: object) -> int:
    amount = require_positive(value)
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))

def from_minor_units(value: object) -> Decimal:
    if isinstance(value, bool):
        raise MoneyError("Invalid minor-unit amount.")
    try:
        return (Decimal(int(value)) / 100).quantize(MINOR_UNIT)
    except (ValueError, TypeError, InvalidOperation) as exc:
        raise MoneyError("Invalid minor-unit amount.") from exc

def format_inr(value: object) -> str:
    return f"₹{to_decimal(value):,.2f}"
