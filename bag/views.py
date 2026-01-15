from django.contrib import messages
from django.shortcuts import HttpResponse, redirect, render, reverse
from products.models import Product


def view_bag(request):
    """Render the bag contents page."""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """Add item to the bag and refresh the product detail page."""
    bag = request.session.get("bag", {})
    quantity = int(request.POST.get("quantity"))
    size = request.POST.get("product_size")
    if size:
        _update_bag_with_sized_items(item_id, bag, quantity, size)
    else:
        _update_bag_with_unsized_items(request, item_id, bag, quantity)
    request.session.modified = True
    return redirect(request.POST.get("redirect_url"))


def adjust_bag(request, item_id):
    """Adjust the quantity of an item in the bag."""
    bag = request.session.get("bag")
    quantity = int(request.POST.get("quantity"))
    size = request.POST.get("product_size")
    if size:
        if quantity > 0:
            bag[item_id]["items_by_size"][size] = quantity
        else:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                del bag[item_id]
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            del bag[item_id]
    request.session.modified = True
    return redirect(reverse("view_bag"))


def remove_from_bag(request, item_id):
    """Remove an item from the bag."""
    try:
        bag = request.session.get("bag")
        size = request.POST.get("product_size")
        if size:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                del bag[item_id]
        else:
            del bag[item_id]
        request.session.modified = True
        return HttpResponse(status=200)
    except Exception:
        return HttpResponse(status=500)


def _update_bag_with_unsized_items(request, item_id, bag, quantity):
    """Update the bag with items that don't have a size."""
    if item_id not in bag:
        bag[item_id] = 0
        product = Product.objects.get(pk=item_id)
        messages.success(request, f"Added {product.name} to your bag!")
    bag[item_id] += quantity


def _update_bag_with_sized_items(item_id, bag, quantity, size):
    """Update the bag with items that have a size."""
    if item_id not in bag:
        bag[item_id] = {"items_by_size": {size: 0}}
    if size not in bag[item_id]["items_by_size"]:
        bag[item_id]["items_by_size"][size] = 0
    bag[item_id]["items_by_size"][size] += quantity
