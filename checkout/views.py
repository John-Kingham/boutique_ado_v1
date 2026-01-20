from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from .forms import OrderForm


def checkout(request):
    """A view for the checkout page."""
    bag = request.session.get("bag")
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse("products"))
    template = "checkout/checkout.html"
    context = {"order_form": OrderForm()}
    return render(request, template, context)
