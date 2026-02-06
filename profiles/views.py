from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .models import UserProfile
from .forms import UserProfileForm


def profile(request):
    """Display the user's profile."""
    template = "profiles/profile.html"
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()
    context = {
        "form": form,
        "orders": orders,
        "on_profile_page": True,
    }
    return render(request, template, context)
