import json
import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from programs.models import Program

from .forms import DonationForm
from .models import Donation
from . import services

logger = logging.getLogger(__name__)


def donate(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {
            "name": request.user.get_full_name() or "",
            "email": request.user.email,
        }
    program_slug = request.GET.get("program")
    if program_slug:
        program = Program.objects.filter(slug=program_slug, is_published=True).first()
        if program:
            initial["program"] = program

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.user = request.user
            donation.status = Donation.Status.CREATED
            donation.save()

            try:
                order = services.create_order(
                    donation.amount_paise,
                    receipt=f"don_{donation.pk}",
                    notes={"donation_id": str(donation.pk), "email": donation.email},
                )
            except Exception:
                # Razorpay API/network error — don't 500; fall back to a pledge.
                logger.exception("Razorpay order creation failed for donation %s", donation.pk)
                order = None

            if order is None:
                # Razorpay not configured (or errored) — fall back to a pledge flow.
                messages.warning(
                    request,
                    "Online payments are not configured yet. Your pledge has been "
                    "recorded and our team will contact you with payment details.",
                )
                return redirect("donations:success", token=donation.token)

            donation.razorpay_order_id = order["id"]
            donation.save(update_fields=["razorpay_order_id"])
            return render(
                request,
                "donations/checkout.html",
                {
                    "donation": donation,
                    "order": order,
                    "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                },
            )
    else:
        form = DonationForm(initial=initial)

    return render(
        request,
        "donations/donate.html",
        {"form": form, "presets": DonationForm.PRESET_AMOUNTS},
    )


def payment_callback(request):
    """Handle the Razorpay Checkout success POST (signature verification)."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    order_id = request.POST.get("razorpay_order_id")
    payment_id = request.POST.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature")
    donation = get_object_or_404(Donation, razorpay_order_id=order_id)

    try:
        services.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
    except Exception:
        donation.status = Donation.Status.FAILED
        donation.save(update_fields=["status"])
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("donations:donate")

    _mark_paid(donation, payment_id, signature)
    messages.success(request, "Thank you! Your donation was successful.")
    return redirect("donations:success", token=donation.token)


def _mark_paid(donation, payment_id="", signature=""):
    if donation.status == Donation.Status.PAID:
        return
    donation.status = Donation.Status.PAID
    donation.razorpay_payment_id = payment_id
    donation.razorpay_signature = signature
    donation.paid_at = timezone.now()
    donation.save()
    # Keep the program's running total in sync.
    if donation.program_id:
        Program.objects.filter(pk=donation.program_id).update(
            raised_amount=F("raised_amount") + donation.amount
        )


def success(request, token):
    donation = get_object_or_404(Donation, token=token)
    return render(request, "donations/success.html", {"donation": donation})


def receipt(request, token):
    # The unguessable token in the URL is the access capability.
    donation = get_object_or_404(Donation, token=token)
    return render(request, "donations/receipt.html", {"donation": donation})


@csrf_exempt
def webhook(request):
    """Backup reconciliation: Razorpay calls this on payment events."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    signature = request.headers.get("X-Razorpay-Signature", "")
    if not services.verify_webhook_signature(request.body, signature):
        return HttpResponse(status=400)

    payload = json.loads(request.body or "{}")
    entity = (
        payload.get("payload", {}).get("payment", {}).get("entity", {})
    )
    order_id = entity.get("order_id")
    payment_id = entity.get("id")
    if order_id:
        donation = Donation.objects.filter(razorpay_order_id=order_id).first()
        if donation and payload.get("event") in {"payment.captured", "order.paid"}:
            _mark_paid(donation, payment_id or "")
    return HttpResponse(status=200)
