"""Thin wrapper around the Razorpay SDK so views stay clean and testable."""
import razorpay
from django.conf import settings


def get_client():
    """Return a configured Razorpay client, or None if keys are not set."""
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET):
        return None
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def create_order(amount_paise, receipt, notes=None):
    """Create a Razorpay order and return its dict, or None if unconfigured."""
    client = get_client()
    if client is None:
        return None
    return client.order.create(
        {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": notes or {},
        }
    )


def verify_payment_signature(params):
    """Verify the checkout callback signature. Raises on failure."""
    client = get_client()
    if client is None:
        raise ValueError("Razorpay is not configured.")
    client.utility.verify_payment_signature(params)


def verify_webhook_signature(body, signature):
    client = get_client()
    if client is None or not settings.RAZORPAY_WEBHOOK_SECRET:
        return False
    try:
        client.utility.verify_webhook_signature(
            body, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
