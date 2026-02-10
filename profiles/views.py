from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order


def profile(request):
    """Display the user's profile."""
    template = "profiles/profile.html"
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(
                request, "Update failed. Please ensure the form is valid."
            )
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all()
    context = {
        "form": form,
        "orders": orders,
        "on_profile_page": True,
    }
    return render(request, template, context)


def order_history(request, order_number):
    """Display the order history template."""
    order = get_object_or_404(Order, order_number=order_number)
    messages.info(
        request,
        (
            f"This is a past confirmation for order number {order_number}. "
            "A confirmation email was sent on the order date."
        ),
    )
    template = "checkout/checkout_success.html"
    context = {
        "order": order,
        "from_profile": True,
    }
    return render(request, template, context)
