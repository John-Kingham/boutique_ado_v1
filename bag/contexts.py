from decimal import Decimal
from django.conf import settings


def bag_contents(request):
    """Return shopping bag context items."""
    bag_items = []
    total = 0
    product_count = 0
    delivery = 0
    free_delivery_delta = 0

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = _delivery_fee(total)
        free_delivery_delta = _free_delivery_gap(total)
    grand_total = total + delivery
    return {
        "bag_items": bag_items,
        "total": total,
        "grand_total": grand_total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
    }


def _free_delivery_gap(total):
    """Return gap between order total and free delivery threshold."""
    return settings.FREE_DELIVERY_THRESHOLD - total


def _delivery_fee(total):
    """
    Return delivery fee based on order total, ignoring free delivery options.
    """
    return total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
