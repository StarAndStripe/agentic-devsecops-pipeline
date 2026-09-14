def calculate_discount(price: float, percentage: float) -> float:
    """Calculate the final price after applying a percentage discount."""
    if price < 0:
        raise ValueError("Price cannot be negative")

    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100")

    return price - (price * percentage / 100)

def calculate_shipping_fee(order_total: float, express: bool = False) -> float:
    """Calculate shipping fee based on order total and delivery type."""
    if order_total < 0:
        raise ValueError("Order total cannot be negative")

    if order_total >= 150:
        return 0

    if express:
        return 15

    return 5