"""URL configuration for fhc project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("gallery/", include("gallery.urls")),
    path("programs/", include("programs.urls")),
    path("blog/", include("blog.urls")),
    path("events/", include("events.urls")),
    path("donate/", include("donations.urls")),
    path("volunteer/", include("volunteers.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
