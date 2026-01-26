from http import HTTPStatus
from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks."""

    def __init__(self, request):
        self.request = request

    def on_unhandled_event(self, event):
        """Handle a generic, unknown or unexpected webhook event."""
        return HttpResponse(
            content=f"Unhandled webhook received: {event["type"]}",
            status=HTTPStatus.OK,
        )

    def on_payment_succeeded(self, event):
        """Handle Stripe's payment_intent.succeeded event."""
        return HttpResponse(
            content=f"Webhook received: {event["type"]}",
            status=HTTPStatus.OK,
        )

    def on_payment_failed(self, event):
        """Handle Stripe's payment_intent.payment_failed event."""
        return HttpResponse(
            content=f"Webhook received: {event["type"]}",
            status=HTTPStatus.OK,
        )
