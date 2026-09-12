def calculate_discount(price: float, percentage: float) -> float:
    """Calculate the final price after applying a percentage discount."""
    if price < 0:
        raise ValueError("Price cannot be negative")

    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100")

    return price - (price * percentage / 100)