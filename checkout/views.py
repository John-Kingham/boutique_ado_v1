from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from .forms import OrderForm
from bag.contexts import bag_contents
import stripe


def checkout(request):
    """A view for the checkout page."""
    bag_is_empty = not request.session.get("bag")
    if bag_is_empty:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse("products"))
    payment_intent = _stripe_payment_intent(request)
    context = {
        "order_form": OrderForm(),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": payment_intent.client_secret,
    }
    return render(request, "checkout/checkout.html", context)


def _stripe_payment_intent(request):
    """Return a Stripe payment intent for the current bag."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    grand_total_in_subunits = round(bag_contents(request)["grand_total"] * 100)
    intent = stripe.PaymentIntent.create(
        amount=grand_total_in_subunits, currency=settings.STRIPE_CURRENCY
    )
    return intent
