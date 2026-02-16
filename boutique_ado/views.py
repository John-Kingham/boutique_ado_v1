from http import HTTPStatus
from django.shortcuts import render


def handler404(request, exception):
    """Handle page not found errors"""
    return render(request, "errors/404.html", status=HTTPStatus.NOT_FOUND)
