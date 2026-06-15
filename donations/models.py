import uuid

from django.conf import settings
from django.db import models


class Donation(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    # Unguessable public identifier used in success/receipt URLs.
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )

    # Donor details (captured even for guests)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    amount = models.PositiveIntegerField(help_text="Amount in INR.")
    currency = models.CharField(max_length=10, default="INR")
    is_recurring = models.BooleanField(default=False)
    message = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.CREATED
    )
    razorpay_order_id = models.CharField(max_length=64, blank=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)
    razorpay_signature = models.CharField(max_length=128, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"₹{self.amount} by {self.name} ({self.get_status_display()})"

    @property
    def receipt_no(self):
        return f"FHC-{self.created:%Y}-{self.pk:05d}"

    @property
    def amount_paise(self):
        return self.amount * 100
