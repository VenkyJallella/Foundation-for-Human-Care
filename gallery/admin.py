from django.contrib import admin

from .forms import AlbumAdminForm
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ("image", "caption", "order")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    list_display = ("title", "photo_count", "is_published", "created")
    list_filter = ("is_published",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PhotoInline]

    @admin.display(description="Photos")
    def photo_count(self, obj):
        return obj.photos.count()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Create a Photo for each file uploaded via the bulk "Upload photos" field.
        for uploaded in form.cleaned_data.get("bulk_photos", []):
            Photo.objects.create(album=form.instance, image=uploaded)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "album", "order", "created")
    list_filter = ("album",)
