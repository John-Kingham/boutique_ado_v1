from django.shortcuts import get_object_or_404, render

from .models import UserProfile


def profile(request):
    """Display the user's profile."""
    template = "profiles/profile.html"
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {"profile": profile}
    return render(request, template, context)
