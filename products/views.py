from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from .models import Category, Product


def all_products(request):
    """
    Show the all products page.

    Show all products by default.
    If the user submitted a search, only show matching products.
    If the search term is blank, show an error message.
    If the user selected categories, only show matching products.
    """

    # Show all products by default
    search_term = None
    categories = None
    products = Product.objects.all()

    # If the user submitted a product search, show matching products.
    # If the search was empty, show an error message.
    if request.GET:
        is_product_search = "q" in request.GET
        if is_product_search:
            search_term = request.GET["q"]
            if search_term:
                query = Q(name__icontains=search_term) | Q(
                    description__icontains=search_term
                )
                products = products.filter(query)
            else:
                messages.error(request, "You didn't enter any search text!")
                return redirect(reverse("products"))

        # If the user selected categories, show matching products.
        is_category_search = "category" in request.GET
        if is_category_search:
            category_names = request.GET["category"].split(",")
            products = products.filter(category__name__in=category_names)
            categories = Category.objects.filter(name__in=category_names)

    # render the page
    context = {
        "products": products,
        "search_term": search_term,
        "categories": categories,
    }
    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """Show the product detail page for a single product."""

    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "products/product_detail.html", context)
