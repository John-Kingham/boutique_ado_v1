from django.shortcuts import redirect, render


def view_bag(request):
    """Render the bag contents page."""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """Add item to bag and refresh the product detail page."""
    bag = request.session.get("bag", {})
    quantity = int(request.POST.get("quantity"))
    size = request.POST.get("product_size")
    if size:
        update_bag_with_sized_items(item_id, bag, quantity, size)
    else:
        update_bag_with_unsized_items(item_id, bag, quantity)
    request.session["bag"] = bag
    return redirect(request.POST.get("redirect_url"))


def update_bag_with_unsized_items(item_id, bag, quantity):
    """Update bag with items that don't have a size."""
    if item_id not in bag:
        bag[item_id] = 0
    bag[item_id] += quantity


def update_bag_with_sized_items(item_id, bag, quantity, size):
    """Update bag with items that have a size."""
    if item_id not in bag:
        bag[item_id] = {"items_by_size": {size: 0}}
    if size not in bag[item_id]["items_by_size"]:
        bag[item_id]["items_by_size"][size] = 0
    bag[item_id]["items_by_size"][size] += quantity
