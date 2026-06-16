from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class EventQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def upcoming(self):
        return self.published().filter(start__gte=timezone.now()).order_by("start")

    def past(self):
        return self.published().filter(start__lt=timezone.now()).order_by("-start")


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(
        default=0, help_text="0 = unlimited seats."
    )
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ("-start",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:detail", args=[self.slug])

    @property
    def is_past(self):
        return self.start < timezone.now()

    @property
    def seats_taken(self):
        # Only active registrations count toward capacity (not cancelled ones).
        return self.registrations.filter(status="registered").count()

    @property
    def is_full(self):
        return self.capacity > 0 and self.seats_taken >= self.capacity


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.REGISTERED
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user} → {self.event}"
