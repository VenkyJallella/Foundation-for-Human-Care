from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ApplicationForm
from .models import Application, Opportunity


def opportunity_list(request):
    opportunities = Opportunity.objects.filter(is_open=True)
    return render(
        request, "volunteers/list.html", {"opportunities": opportunities}
    )


def opportunity_detail(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug)
    already_applied = False
    if request.user.is_authenticated:
        already_applied = Application.objects.filter(
            opportunity=opportunity, user=request.user
        ).exists()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Please log in or register to volunteer.")
            return redirect("accounts:login")
        if already_applied:
            messages.info(request, "You've already applied to this opportunity.")
            return redirect(opportunity.get_absolute_url())
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.opportunity = opportunity
            application.user = request.user
            application.save()
            messages.success(
                request, "Thanks for applying! We'll review your application soon."
            )
            return redirect(opportunity.get_absolute_url())
    else:
        form = ApplicationForm()

    return render(
        request,
        "volunteers/detail.html",
        {
            "opportunity": opportunity,
            "form": form,
            "already_applied": already_applied,
        },
    )
