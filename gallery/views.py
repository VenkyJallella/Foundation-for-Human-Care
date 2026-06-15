from django.shortcuts import get_object_or_404, render

from .models import Album


def album_list(request):
    albums = Album.objects.filter(is_published=True).prefetch_related("photos")
    return render(request, "gallery/list.html", {"albums": albums})


def album_detail(request, slug):
    album = get_object_or_404(Album, slug=slug, is_published=True)
    return render(request, "gallery/detail.html", {"album": album})
