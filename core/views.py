from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ContactForm, NewsletterForm


def home(request):
    from blog.models import Post
    from events.models import Event
    from programs.models import Program

    context = {
        "featured_programs": Program.objects.filter(
            is_published=True, is_featured=True
        )[:3],
        "recent_posts": Post.objects.filter(status=Post.Status.PUBLISHED)[:3],
        "upcoming_events": Event.objects.upcoming()[:3],
        "newsletter_form": NewsletterForm(),
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            _notify_contact(message)
            messages.success(
                request, "Thank you for reaching out. We'll get back to you soon."
            )
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})


def _notify_contact(message):
    """Email the team when someone submits the contact form."""
    subject = f"[Contact] {message.subject or 'New message'} — from {message.name}"
    body = (
        f"You received a new message from the website contact form.\n\n"
        f"Name:    {message.name}\n"
        f"Email:   {message.email}\n"
        f"Subject: {message.subject or '(none)'}\n"
        f"Sent:    {message.created:%d %b %Y, %I:%M %p}\n\n"
        f"Message:\n{message.message}\n"
    )
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_NOTIFICATION_EMAIL],
        reply_to=[message.email],  # so you can reply straight to the sender
    )
    # Never let an email failure break the form submission for the visitor.
    email.send(fail_silently=True)


def newsletter_subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You're subscribed to our newsletter!")
        else:
            messages.error(
                request, form.errors.get("email", ["Invalid email."])[0]
            )
    # Return to the page the visitor came from, but only if it's our own site.
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect("core:home")
