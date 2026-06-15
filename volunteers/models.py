from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Opportunity(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    skills = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated skills (optional)."
    )
    openings = models.PositiveIntegerField(default=1)
    is_open = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ("-created",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("volunteers:detail", args=[self.slug])

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="applications"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="volunteer_applications",
    )
    message = models.TextField(blank=True, help_text="Why do you want to help?")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.APPLIED
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("opportunity", "user")
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user} → {self.opportunity}"
