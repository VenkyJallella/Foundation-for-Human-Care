import re

from django.db import models


class SiteSetting(models.Model):
    """Singleton holding global, admin-editable site content."""

    org_name = models.CharField(max_length=120, default="Foundation for Human Care")
    tagline = models.CharField(max_length=200, blank=True)
    about_short = models.TextField(blank=True, help_text="Short blurb shown on the home page.")
    about_long = models.TextField(blank=True, help_text="Full text shown on the About page.")
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)

    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.CharField(max_length=300, blank=True)
    hero_image = models.ImageField(upload_to="site/", blank=True, null=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)

    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # Founder
    founder_name = models.CharField(max_length=120, blank=True)
    founder_role = models.CharField(max_length=120, blank=True)
    founder_message = models.TextField(
        blank=True, help_text="A short note from the founder shown on the About page."
    )
    founder_photo = models.ImageField(upload_to="site/", blank=True, null=True)

    # Impact stats shown on the home page
    stat_people_helped = models.PositiveIntegerField(default=0)
    stat_volunteers = models.PositiveIntegerField(default=0)
    stat_projects = models.PositiveIntegerField(default=0)
    stat_funds_raised = models.PositiveIntegerField(default=0)

    # Bank / UPI details (shown as a fallback giving option)
    bank_details = models.TextField(blank=True)

    # Legal / registration (shown on receipts & policy pages when filled in)
    legal_name = models.CharField(
        max_length=200, blank=True,
        help_text="Registered legal name, if different from the display name.",
    )
    pan_number = models.CharField("PAN", max_length=20, blank=True)
    registration_number = models.CharField(
        max_length=80, blank=True,
        help_text="Trust / Society / Section 8 registration number.",
    )
    reg_12a_number = models.CharField("12A registration no.", max_length=80, blank=True)
    reg_80g_number = models.CharField("80G registration no.", max_length=80, blank=True)

    # Policy pages (admin-editable; sensible defaults shown if left blank)
    privacy_policy = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    refund_policy = models.TextField(blank=True)

    class Meta:
        verbose_name = "Site setting"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.org_name

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # never delete the singleton

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_number(self):
        """Digits-only phone (incl. country code) for wa.me links; '' if unset."""
        return re.sub(r"\D", "", self.phone or "")


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.name} — {self.subject or 'No subject'}"


class Document(models.Model):
    """Public transparency documents — annual reports, certificates, etc."""

    class Category(models.TextChoices):
        ANNUAL_REPORT = "annual_report", "Annual Report"
        FINANCIAL = "financial", "Financial Statement"
        CERTIFICATE = "certificate", "Registration / Certificate"
        POLICY = "policy", "Policy"
        OTHER = "other", "Other"

    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    file = models.FileField(upload_to="documents/")
    description = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)
    uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("category", "-uploaded")

    def __str__(self):
        return self.title
