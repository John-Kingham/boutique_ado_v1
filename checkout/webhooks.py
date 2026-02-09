from http import HTTPStatus
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
from .webhook_handler import StripeWH_Handler


@require_POST  # Only allow POST requests
@csrf_exempt  # Skip csrf enforcement as Stripe doesn't send a csrf token
def webhook(request):
    """Listen for and handle webhook events from Stripe."""
    event = None
    try:
        event = _get_stripe_event(request)
    except ValueError as payload_error:  # noqa: F841
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    except Exception as exception:
        return HttpResponse(content=exception, status=HTTPStatus.BAD_REQUEST)
    response = _handle_event(request, event)
    return response


def _handle_event(request, event):
    wh_handler = StripeWH_Handler(request)
    event_handler_map = {
        "payment_intent.succeeded": wh_handler.handle_payment_succeeded,
        "payment_intent.payment_failed": wh_handler.handle_payment_failed,
    }
    handler_method = event_handler_map.get(
        event["type"], wh_handler.handle_other_event
    )
    response = handler_method(event)
    return response


def _get_stripe_event(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.Webhook.construct_event(
        request.body,
        request.META["HTTP_STRIPE_SIGNATURE"],
        settings.STRIPE_WH_SECRET,
    )
