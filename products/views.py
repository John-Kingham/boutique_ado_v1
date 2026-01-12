from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render, reverse
from .models import Category, Product


def all_products(request):
    """
    Show the products page.

    Show all products by default.
    If the user submitted a search, only show matching products. If the search
    term is blank, show an error message.
    If the user selected a sort option, show sorted products.
    If the user selected categories, show matching products.
    """

    context = _default_context_for_all_products()
    if request.GET and "q" in request.GET:
        search_term = request.GET["q"]
        if search_term:
            _update_context_for_search(search_term, context)
        else:
            messages.error(request, "You didn't enter any search text!")
            return redirect(reverse("products"))
    if request.GET and "sort" in request.GET:
        _update_context_for_sort(request, context)
    if request.GET and "category" in request.GET:
        _update_context_for_category_filter(request, context)
    return render(request, "products/products.html", context)


def _update_context_for_category_filter(request, context):
    """Update the context to filter products by category."""
    category_names = request.GET["category"].split(",")
    context["products"] = context["products"].filter(
        category__name__in=category_names
    )
    context["current_categories"] = Category.objects.filter(
        name__in=category_names
    )


def _update_context_for_sort(request, context):
    """Update the context to sort products."""
    products = context["products"]
    sort = request.GET["sort"]
    direction = request.GET.get("direction")
    sortkey = sort
    if sort == "name":
        products = products.annotate(lower_name=Lower("name"))
        sortkey = "lower_name"
    elif sort == "category":
        sortkey = "category__name"
    if direction == "desc":
        sortkey = f"-{sortkey}"
    products = products.order_by(sortkey)
    context["products"] = products
    context["current_sorting"] = f"{sort}_{direction}"


def _default_context_for_all_products():
    """
    Return the default context for the products page.

    By default, the page shows all products for all categories with no sort or
    selection.
    """
    return {
        "products": Product.objects.all(),
        "search_term": None,
        "current_categories": None,
        "current_sorting": f"{None}_{None}",
    }


def _update_context_for_search(search_term, context):
    """Update the context to filter products for a search."""
    context["search_term"] = search_term
    context["products"] = context["products"].filter(
        Q(name__icontains=search_term) | Q(description__icontains=search_term)
    )


def product_detail(request, product_id):
    """Show the product detail page for a single product."""
    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "products/product_detail.html", context)
