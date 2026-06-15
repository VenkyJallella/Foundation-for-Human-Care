from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Album(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="gallery/covers/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("gallery:detail", args=[self.slug])

    @property
    def cover_image(self):
        if self.cover:
            return self.cover
        first = self.photos.first()
        return first.image if first else None


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="gallery/photos/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "created")

    def __str__(self):
        return self.caption or f"Photo #{self.pk}"
