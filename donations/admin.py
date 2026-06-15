from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_no", "name", "email", "amount", "program",
        "status", "is_recurring", "created",
    )
    list_filter = ("status", "is_recurring", "currency", "created")
    search_fields = ("name", "email", "razorpay_order_id", "razorpay_payment_id")
    date_hierarchy = "created"
    readonly_fields = (
        "razorpay_order_id", "razorpay_payment_id", "razorpay_signature",
        "created", "paid_at", "receipt_no",
    )

    def has_add_permission(self, request):
        return False  # donations are created through the public flow only
