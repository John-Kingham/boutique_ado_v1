def product_error_message():
    return (
        "One of the products in your bag wasn't in our database. "
        "Please call us for assistance!"
    )


def form_error_message():
    return (
        "There was an error with your form. "
        "Please double check your information."
    )


def empty_bag_error_message():
    return "There's nothing in your bag at the moment."


def order_success_message(order):
    return (
        "Order successfully processed! "
        f"Your order number is {order.order_number}. "
        f"A confirmation email will be sent to {order.email}."
    )
