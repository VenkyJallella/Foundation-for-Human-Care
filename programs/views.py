from django.shortcuts import get_object_or_404, render

from .models import Program


def program_list(request):
    programs = Program.objects.filter(is_published=True)
    return render(request, "programs/list.html", {"programs": programs})


def program_detail(request, slug):
    program = get_object_or_404(Program, slug=slug, is_published=True)
    others = Program.objects.filter(is_published=True).exclude(pk=program.pk)[:3]
    return render(
        request, "programs/detail.html", {"program": program, "others": others}
    )
