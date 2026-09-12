from src.pricing import calculate_discount
from src.pricing import calculate_shipping_fee

def test_calculate_discount():
    assert calculate_discount(100, 20) == 80


def test_zero_discount():
    assert calculate_discount(100, 0) == 100


def test_full_discount():
    assert calculate_discount(100, 100) == 0


def test_standard_shipping():
    assert calculate_shipping_fee(50) == 5