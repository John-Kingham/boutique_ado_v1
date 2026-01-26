from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
import stripe

from .checkout_messages import (
    empty_bag_error_message,
    form_error_message,
    order_success_message,
    product_error_message,
)
from .forms import OrderForm
from .models import Order, OrderLineItem  # noqa: F401
from bag.contexts import bag_contents
from products.models import Product


def checkout(request):
    """A view for the checkout page."""
    if request.method == "POST":
        response = _save_order(request)
        return response
    bag_is_empty = not request.session.get("bag")
    if bag_is_empty:
        messages.error(request, empty_bag_error_message())
        return redirect(reverse("products"))
    context = {
        "order_form": OrderForm(),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": _payment_intent(request).client_secret,
    }
    template = "checkout/checkout.html"
    return render(request, template, context)


def _payment_intent(request):
    """Return a Stripe payment intent for the current bag."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    grand_total_in_subunits = round(bag_contents(request)["grand_total"] * 100)
    intent = stripe.PaymentIntent.create(
        amount=grand_total_in_subunits, currency=settings.STRIPE_CURRENCY
    )
    return intent


def _save_order(request):
    """
    Save an order from a post request.

    Return (HTTPRedirectResponse): Redirect user to the next page.
    """
    bag = request.session.get("bag", {})
    order_form = OrderForm(_form_data(request))
    if order_form.is_valid():
        order = order_form.save()
        for item_id, item_data in bag.items():
            try:
                _add_order_line_item(order, item_id, item_data)
            except Product.DoesNotExist:
                order.delete()
                messages.error(request, product_error_message())
                return redirect(reverse("view_bag"))
        request.session["save_info"] = "save-info" in request.POST
        return redirect(reverse("checkout_success", args=[order.order_number]))
    else:
        messages.error(request, form_error_message)
        return redirect(reverse("view_bag"))


def _add_order_line_item(order, item_id, item_data):
    """Add an order line item to the order."""
    product = Product.objects.get(id=item_id)
    if isinstance(item_data, int):
        order_line_item = OrderLineItem(
            order=order,
            product=product,
            quantity=item_data,
        )
        order_line_item.save()
    else:
        for size, quantity in item_data["items_by_size"].items():
            order_line_item = OrderLineItem(
                order=order,
                product=product,
                quantity=quantity,
                product_size=size,
            )
            order_line_item.save()


def _form_data(request):
    """Return a dict of form data extracted from the post request."""
    return {
        "full_name": request.POST["full_name"],
        "email": request.POST["email"],
        "phone_number": request.POST["phone_number"],
        "country": request.POST["country"],
        "postcode": request.POST["postcode"],
        "town_or_city": request.POST["town_or_city"],
        "street_address1": request.POST["street_address1"],
        "street_address2": request.POST["street_address2"],
        "county": request.POST["county"],
    }


def checkout_success(request, order_number):
    """Handle successful checkouts."""
    # save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, order_success_message(order))
    request.session.pop("bag", None)
    return render(request, "checkout/checkout_success.html", {"order": order})
