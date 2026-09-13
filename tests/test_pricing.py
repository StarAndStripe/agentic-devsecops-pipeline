from src.pricing import calculate_discount
from src.pricing import calculate_shipping_fee
import pytest


def test_calculate_discount():
    assert calculate_discount(100, 20) == 80


def test_zero_discount():
    assert calculate_discount(100, 0) == 100


def test_full_discount():
    assert calculate_discount(100, 100) == 0


def test_standard_shipping():
    assert calculate_shipping_fee(50) == 5


def test_express_shipping():
    assert calculate_shipping_fee(50, express=True) == 15


def test_free_shipping_at_boundary():
    assert calculate_shipping_fee(100) == 0


def test_free_shipping_above_threshold():
    assert calculate_shipping_fee(150) == 0


def test_negative_order_total():
    with pytest.raises(ValueError, match="Order total cannot be negative"):
        calculate_shipping_fee(-1)