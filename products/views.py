from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render, reverse
from .models import Category, Product


def all_products(request):
    """
    Show the products page.

    Show all products by default.
    If the user submitted a search, show matching products. If the search
    term is blank, show an error message.
    If the user selected a sort option, show sorted products.
    If the user selected a category, show matching products.
    """

    # Show all products by default
    search_term = None
    categories = None
    sort = None
    direction = None
    products = Product.objects.all()

    if request.GET:

        # If user submitted a search, show matching products. If the search
        # term is empty, show an error message.
        if "q" in request.GET:
            search_term = request.GET["q"]
            if search_term:
                products = products.filter(
                    Q(name__icontains=search_term)
                    | Q(description__icontains=search_term)
                )
            else:
                messages.error(request, "You didn't enter any search text!")
                return redirect(reverse("products"))

        # If user selected a sort option, show sorted products.
        if "sort" in request.GET:
            sort = request.GET["sort"]
            direction = request.GET.get("direction")
            sortkey = sort
            # If sorting by alpha field, use lowercase sort
            if sort == "name":
                products = products.annotate(lower_name=Lower("name"))
                sortkey = "lower_name"
            # if sorting by category, sort by category name (not id)
            if sort == "category":
                sortkey = "category__name"
            if direction == "desc":
                sortkey = f"-{sortkey}"
            products = products.order_by(sortkey)

        # If user selected a category, show matching products.
        if "category" in request.GET:
            category_names = request.GET["category"].split(",")
            products = products.filter(category__name__in=category_names)
            categories = Category.objects.filter(name__in=category_names)

    # render the page
    context = {
        "products": products,
        "search_term": search_term,
        "current_categories": categories,
        "current_sorting": f"{sort}_{direction}",
    }
    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """Show the product detail page for a single product."""

    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "products/product_detail.html", context)
