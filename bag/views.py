from django.shortcuts import redirect, render


def view_bag(request):
    """Render the bag contents page."""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """Add item(s) to bag and refresh the product detail page."""
    quantity = int(request.POST.get("quantity"))
    bag = request.session.get("bag", {})
    if item_id not in bag:
        bag[item_id] = 0
    bag[item_id] += quantity
    request.session["bag"] = bag
    return redirect(request.POST.get("redirect_url"))
