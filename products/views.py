from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from .models import Product


def all_products(request):
    """
    Show the all products page.

    Show all products by default. If this is a get request with a search term,
    only show matching products. If the search term is blank, show an error
    message.
    """

    # Show all products by default
    products = Product.objects.all()
    search_term = None

    # If the user submitted a search, only show matching products. If the
    # search term was blank, show an error message.
    if request.GET and "q" in request.GET:
        search_term = request.GET["q"]
        if search_term:
            query = Q(name__icontains=search_term) | Q(
                description__icontains=search_term
            )
            products = products.filter(query)
        else:
            messages.error(request, "You didn't enter any search text!")
            return redirect(reverse("products"))

    context = {"products": products, "search_term": search_term}
    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """Show the product detail page for a single product."""

    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "products/product_detail.html", context)
