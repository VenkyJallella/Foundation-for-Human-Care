from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, Post


def _published():
    return Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
        "category", "author"
    )


def post_list(request):
    posts = _published()
    paginator = Paginator(posts, 6)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "blog/list.html",
        {"page_obj": page, "categories": Category.objects.all()},
    )


def post_detail(request, slug):
    post = get_object_or_404(_published(), slug=slug)
    related = _published().exclude(pk=post.pk)[:3]
    return render(request, "blog/detail.html", {"post": post, "related": related})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = _published().filter(category=category)
    paginator = Paginator(posts, 6)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "blog/list.html",
        {
            "page_obj": page,
            "categories": Category.objects.all(),
            "active_category": category,
        },
    )
