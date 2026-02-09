from http import HTTPStatus
import json

from django.conf import settings
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    HttpResponse,
    redirect,
    render,
    reverse,
)
from django.views.decorators.http import require_POST
import stripe

from bag.contexts import bag_contents
from products.models import Product
from profiles.forms import UserProfileForm
from profiles.models import UserProfile

from .checkout_messages import (
    empty_bag_error_message,
    form_error_message,
    order_success_message,
    payment_error_message,
    product_error_message,
)
from .forms import OrderForm
from .models import Order, OrderLineItem  # noqa: F401


def checkout(request):
    """A view for the checkout page."""
    if request.method == "POST":
        response = _save_order(request)
        return response
    bag_is_empty = not request.session.get("bag")
    if bag_is_empty:
        messages.error(request, empty_bag_error_message())
        return redirect(reverse("products"))

    # Initialise order form
    order_form = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(
                initial={
                    "full_name": profile.user.get_full_name(),
                    "email": profile.user.email,
                    "phone_number": profile.default_phone_number,
                    "country": profile.default_country,
                    "postcode": profile.default_postcode,
                    "town_or_city": profile.default_town_or_city,
                    "street_address1": profile.default_street_address1,
                    "street_address2": profile.default_street_address2,
                    "county": profile.default_county,
                }
            )
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
    else:
        order_form = OrderForm()

    context = {
        "order_form": order_form,
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
    order_form = OrderForm(_order_form_data(request))
    if order_form.is_valid():
        order = order_form.save(commit=False)
        pid = request.POST.get("client_secret").split("_secret")[0]
        order.stripe_pid = pid
        order.original_bag = json.dumps(bag)
        order.save()
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


def _order_form_data(request):
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
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        # Attach the user's profile to the order
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, order_success_message(order))
    request.session.pop("bag", None)
    return render(request, "checkout/checkout_success.html", {"order": order})


@require_POST
def cache_checkout_data(request):
    """Cache data when the checkout form is submitted."""
    try:
        payment_id = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            payment_id,
            metadata={
                "bag": json.dumps(request.session.get("bag", {})),
                "save_info": request.POST.get("save_info"),
                "username": request.user.username,
            },
        )
        return HttpResponse(status=HTTPStatus.OK)
    except Exception as error:
        messages.error(request, payment_error_message())
        return HttpResponse(content=error, status=HTTPStatus.BAD_REQUEST)
