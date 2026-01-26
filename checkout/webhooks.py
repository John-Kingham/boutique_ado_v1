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
    except ValueError:
        # Invalid payload
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    except Exception as exception:
        return HttpResponse(content=exception, status=HTTPStatus.BAD_REQUEST)
    response = handle_event(request, event)
    return response


def handle_event(request, event):
    handler_object = StripeWH_Handler(request)
    event_handler_map = {
        "payment_intent.succeeded": handler_object.on_payment_succeeded,
        "payment_intent.payment_failed": handler_object.on_payment_failed,
    }
    handler_method = event_handler_map.get(
        event["type"], handler_object.on_unhandled_event
    )
    response = handler_method(event)
    return response


def _get_stripe_event(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.Webhook.construct_event(payload, sig_header, wh_secret)
