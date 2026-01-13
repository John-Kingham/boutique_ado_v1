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
    for item_id, item_data in bag.items():
        _update_context_for_bag_item(context, item_id, item_data)
    _update_context_for_delivery(context)
    return context


def _update_context_for_delivery(context):
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


def _update_context_for_bag_item(context, item_id, item_data):
    """Update context for a shopping bag item."""
    product = get_object_or_404(Product, pk=item_id)
    items_by_size = _get_items_by_size(item_data)
    for size, quantity in items_by_size.items():
        context["total"] += product.price * quantity
        context["product_count"] += quantity
        item_details = {
            "item_id": item_id,
            "quantity": quantity,
            "product": product,
        }
        if size:
            item_details["size"] = size
        context["bag_items"].append(item_details)


def _get_items_by_size(item_data):
    """
    Return a dict of size: quantity.

    If the item has no size, return "": quantity.
    """
    item_data_is_quantity = isinstance(item_data, int)
    if item_data_is_quantity:
        size = ""
        quantity = item_data
        return {size: quantity}
    else:
        return item_data["items_by_size"]


def _free_delivery_gap(total):
    """Return gap between order total and free delivery threshold."""
    return settings.FREE_DELIVERY_THRESHOLD - total


def _delivery_fee(total):
    """
    Return delivery fee based on order total, ignoring free delivery options.
    """
    return total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
