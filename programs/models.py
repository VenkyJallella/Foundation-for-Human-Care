from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Program(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(max_length=300, help_text="Short one-line description.")
    body = models.TextField()
    image = models.ImageField(upload_to="programs/", blank=True, null=True)

    goal_amount = models.PositiveIntegerField(
        default=0, help_text="Fundraising goal in INR (0 = no goal shown)."
    )
    raised_amount = models.PositiveIntegerField(
        default=0, help_text="Amount raised so far in INR."
    )

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "-created")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("programs:detail", args=[self.slug])

    @property
    def progress_percent(self):
        if not self.goal_amount:
            return 0
        return min(round(self.raised_amount / self.goal_amount * 100), 100)
