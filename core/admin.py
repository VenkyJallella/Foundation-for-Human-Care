from django.contrib import admin

from .models import ContactMessage, Document, NewsletterSubscriber, SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Organisation", {"fields": ("org_name", "tagline", "about_short", "about_long", "mission", "vision")}),
        ("Hero (home page banner)", {"fields": ("hero_title", "hero_subtitle", "hero_image")}),
        ("Founder", {"fields": ("founder_name", "founder_role", "founder_message", "founder_photo")}),
        ("Impact stats", {"fields": ("stat_people_helped", "stat_volunteers", "stat_projects", "stat_funds_raised")}),
        ("Contact", {"fields": ("email", "phone", "address", "bank_details")}),
        ("Social links", {"fields": ("facebook", "instagram", "twitter", "youtube")}),
        ("Legal & registration", {
            "fields": ("legal_name", "pan_number", "registration_number", "reg_12a_number", "reg_80g_number"),
            "description": "Shown on donation receipts and policy pages once filled in.",
        }),
        ("Policy pages", {
            "fields": ("privacy_policy", "terms_conditions", "refund_policy"),
            "description": "Leave blank to show built-in starter text; edit to customise.",
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        # Singleton: only allow editing the one row.
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "uploaded")
    list_filter = ("category", "is_published")
    search_fields = ("title", "description")
    list_editable = ("is_published",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created")
    search_fields = ("email",)
    ordering = ("-created",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created", "handled")
    list_filter = ("handled", "created")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("handled",)
    readonly_fields = ("name", "email", "subject", "message", "created")
