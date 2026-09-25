from decimal import Decimal
import pytest

from utils.money import MoneyError, format_inr, to_decimal, to_minor_units

def test_decimal_precision():
    assert to_decimal("100.10") + to_decimal("0.20") == Decimal("100.30")

def test_minor_units():
    assert to_minor_units("100.50") == 10050

def test_zero_and_negative_rejected():
    with pytest.raises(MoneyError):
        to_minor_units("0")
    with pytest.raises(MoneyError):
        to_minor_units("-1")

def test_format():
    assert format_inr("1000.50") == "₹1,000.50"




