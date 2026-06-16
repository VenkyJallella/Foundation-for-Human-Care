from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Event, EventRegistration


def event_list(request):
    return render(
        request,
        "events/list.html",
        {"upcoming": Event.objects.upcoming(), "past": Event.objects.past()},
    )


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            event=event,
            user=request.user,
            status=EventRegistration.Status.REGISTERED,
        ).exists()
    return render(
        request,
        "events/detail.html",
        {"event": event, "is_registered": is_registered},
    )


@login_required
def register(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    if request.method != "POST":
        return redirect(event.get_absolute_url())

    if event.is_past:
        messages.error(request, "This event has already taken place.")
        return redirect(event.get_absolute_url())

    existing = EventRegistration.objects.filter(
        event=event, user=request.user
    ).first()
    if existing and existing.status == EventRegistration.Status.REGISTERED:
        messages.info(request, "You're already registered for this event.")
        return redirect(event.get_absolute_url())

    # Check capacity BEFORE creating the registration row.
    if event.is_full:
        messages.error(request, "Sorry, this event is full.")
        return redirect(event.get_absolute_url())

    if existing:  # re-registering after a previous cancellation
        existing.status = EventRegistration.Status.REGISTERED
        existing.save()
    else:
        EventRegistration.objects.create(
            event=event,
            user=request.user,
            status=EventRegistration.Status.REGISTERED,
        )
    messages.success(request, f"You're registered for {event.title}!")
    return redirect(event.get_absolute_url())


@login_required
def cancel(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        EventRegistration.objects.filter(event=event, user=request.user).update(
            status=EventRegistration.Status.CANCELLED
        )
        messages.success(request, "Your registration has been cancelled.")
    return redirect(event.get_absolute_url())
