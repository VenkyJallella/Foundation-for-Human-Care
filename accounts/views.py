from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegisterForm, UserForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="accounts.backends.EmailBackend")
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("accounts:dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    # Imported here to avoid circular imports at module load time.
    from donations.models import Donation
    from events.models import EventRegistration
    from volunteers.models import Application

    user = request.user
    donations = Donation.objects.filter(user=user).order_by("-created")
    context = {
        "donations": donations[:5],
        "total_donated": sum(
            (d.amount for d in donations if d.status == Donation.Status.PAID), 0
        ),
        "applications": Application.objects.filter(user=user).select_related(
            "opportunity"
        )[:5],
        "registrations": EventRegistration.objects.filter(user=user).select_related(
            "event"
        )[:5],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def my_donations(request):
    from donations.models import Donation

    donations = Donation.objects.filter(user=request.user).order_by("-created")
    return render(request, "accounts/my_donations.html", {"donations": donations})


@login_required
def my_volunteering(request):
    from volunteers.models import Application

    applications = Application.objects.filter(user=request.user).select_related(
        "opportunity"
    )
    return render(
        request, "accounts/my_volunteering.html", {"applications": applications}
    )


@login_required
def my_events(request):
    from events.models import EventRegistration

    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related("event")
    return render(request, "accounts/my_events.html", {"registrations": registrations})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        uform = UserForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:edit_profile")
    else:
        uform = UserForm(instance=request.user)
        pform = ProfileForm(instance=profile)
    return render(
        request, "accounts/edit_profile.html", {"uform": uform, "pform": pform}
    )
