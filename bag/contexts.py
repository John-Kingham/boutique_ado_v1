from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    """Return shopping bag context items."""
    context = {
        "bag_items": [],
        "delivery": 0,
        "free_delivery_delta": 0,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": 0,
        "product_count": 0,
        "total": 0,
    }
    bag = request.session.get("bag", {})
    for item_id, item_quantity in bag.items():
        update_context_for_bag_item(context, item_id, item_quantity)
    update_context_for_delivery(context)
    return context


def update_context_for_delivery(context):
    """
    Update bag context based on delivery fee.

    Update free_delivery_delta and grand_total.
    """
    total = context["total"]
    delivery = context["delivery"]
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = _delivery_fee(total)
        context["free_delivery_delta"] = _free_delivery_gap(total)
    context["grand_total"] = total + delivery


def update_context_for_bag_item(context, item_id, item_quantity):
    """Update context for a shopping bag item."""
    product = get_object_or_404(Product, pk=item_id)
    context["total"] += product.price * item_quantity
    context["product_count"] += item_quantity
    context["bag_items"].append(
        {
            "item_id": item_id,
            "quantity": item_quantity,
            "product": product,
        }
    )


def _free_delivery_gap(total):
    """Return gap between order total and free delivery threshold."""
    return settings.FREE_DELIVERY_THRESHOLD - total


def _delivery_fee(total):
    """
    Return delivery fee based on order total, ignoring free delivery options.
    """
    return total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
