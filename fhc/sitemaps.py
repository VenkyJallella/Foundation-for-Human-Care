from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from events.models import Event
from gallery.models import Album
from programs.models import Program


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return [
            "core:home", "core:about", "core:contact",
            "programs:list", "gallery:list", "blog:list",
            "events:list", "volunteers:list", "donations:donate",
        ]

    def location(self, item):
        return reverse(item)


class ProgramSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Program.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created


class PostSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.published_at


class EventSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Event.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created


class AlbumSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return Album.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created


SITEMAPS = {
    "static": StaticViewSitemap,
    "programs": ProgramSitemap,
    "blog": PostSitemap,
    "events": EventSitemap,
    "gallery": AlbumSitemap,
}
