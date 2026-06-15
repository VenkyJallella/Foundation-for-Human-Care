"""URL configuration for fhc project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from fhc.sitemaps import SITEMAPS

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
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
