from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    HttpResponse,
    redirect,
    render,
    reverse,
)
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
        _update_bag_with_sized_items(request, item_id, bag, quantity, size)
    else:
        _update_bag_with_unsized_items(request, item_id, bag, quantity)
    request.session["bag"] = bag
    return redirect(request.POST.get("redirect_url"))


def adjust_bag(request, item_id):
    """Adjust the quantity of an item in the bag."""
    bag = request.session.get("bag")
    quantity = int(request.POST.get("quantity"))
    size = request.POST.get("product_size")
    product = get_object_or_404(Product, pk=item_id)
    message = None
    if size:
        if quantity > 0:
            bag[item_id]["items_by_size"][size] = quantity
            message = (
                f"Updated {product.name} size {size.upper()} "
                f"quantity to {quantity}!"
            )
        else:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                del bag[item_id]
            message = f"Removed {product.name} size {size.upper()} from bag!"
    else:
        if quantity > 0:
            bag[item_id] = quantity
            message = f"Updated {product.name} quantity to {quantity}!"
        else:
            del bag[item_id]
            message = f"Removed {product.name} from bag!"
    messages.success(request, message)
    request.session["bag"] = bag
    return redirect(reverse("view_bag"))


def remove_from_bag(request, item_id):
    """Remove an item from the bag."""
    try:
        product = get_object_or_404(Product, pk=item_id)
        bag = request.session.get("bag")
        size = request.POST.get("product_size")
        message = None
        if size:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                del bag[item_id]
            message = f"Removed {product.name} size {size.upper()} from bag!"
        else:
            del bag[item_id]
            message = f"Removed {product.name} from bag!"
        messages.success(request, message)
        request.session.modified = True
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f"Error removing item: {e}")
        return HttpResponse(status=500)


def _update_bag_with_unsized_items(request, item_id, bag, quantity):
    """Update the bag with items that don't have a size."""
    product = get_object_or_404(Product, pk=item_id)
    message = None
    if item_id in bag:
        bag[item_id] += quantity
        message = f"Updated {product.name} quantity to {bag[item_id]}"
    else:
        bag[item_id] = quantity
        message = f"Added {product.name} to your bag!"
    messages.success(request, message)


def _update_bag_with_sized_items(request, item_id, bag, quantity, size):
    """Update the bag with items that have a size."""
    product = get_object_or_404(Product, pk=item_id)
    message = None
    if item_id in bag:
        if size in bag[item_id]["items_by_size"]:
            bag[item_id]["items_by_size"][size] += quantity
            message = (
                f"Updated {product.name} size {size.upper()} "
                f"quantity to {bag[item_id]["items_by_size"][size]}"
            )
        else:
            bag[item_id]["items_by_size"][size] = quantity
            message = f"Added {product.name} size {size.upper()} to your bag!"
    else:
        bag[item_id] = {"items_by_size": {size: quantity}}
        message = f"Added {product.name} size {size.upper()} to your bag!"
    messages.success(request, message)
