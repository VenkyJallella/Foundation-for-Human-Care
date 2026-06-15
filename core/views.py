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


def _legal_page(request, title, custom_text, default_text):
    return render(
        request,
        "core/legal_page.html",
        {"page_title": title, "body": custom_text.strip() or default_text},
    )


def privacy(request):
    from .models import SiteSetting

    org = SiteSetting.load()
    default = (
        f"{org.org_name} respects your privacy. We collect only the information you "
        "provide (such as name, email and phone) when you donate, register, volunteer "
        "or contact us, and we use it solely to carry out our charitable work and to "
        "communicate with you.\n\n"
        "We do not sell or rent your personal information to anyone. Online payments "
        "are processed securely by our payment partner (Razorpay); we do not store "
        "your card or bank details on our servers.\n\n"
        "You may request access to, correction of, or deletion of your personal data "
        f"at any time by contacting us at {org.email or 'our contact email'}."
    )
    return _legal_page(request, "Privacy Policy", org.privacy_policy, default)


def terms(request):
    from .models import SiteSetting

    org = SiteSetting.load()
    default = (
        f"By using the {org.org_name} website you agree to these terms.\n\n"
        "The content on this site is provided for information about our charitable "
        "activities. Donations made through this site are voluntary contributions to "
        f"support the work of {org.org_name} and are used at the organisation's "
        "discretion towards its charitable objectives.\n\n"
        "We make every effort to keep information accurate and up to date, but we make "
        "no warranties as to its completeness. We reserve the right to update these "
        "terms at any time."
    )
    return _legal_page(request, "Terms & Conditions", org.terms_conditions, default)


def refund(request):
    from .models import SiteSetting

    org = SiteSetting.load()
    default = (
        "Donations are voluntary contributions and are generally non-refundable.\n\n"
        "If you believe a donation was made in error, or you were charged incorrectly "
        "(for example a duplicate transaction), please contact us within 7 days at "
        f"{org.email or 'our contact email'} with the transaction details. Genuine "
        "erroneous or duplicate payments will be reviewed and, where appropriate, "
        "refunded to the original payment method within 5–7 working days.\n\n"
        "Once a donation receipt has been issued for tax purposes, a refund may not be "
        "possible."
    )
    return _legal_page(request, "Refund & Cancellation Policy", org.refund_policy, default)


def documents(request):
    from .models import Document

    docs = Document.objects.filter(is_published=True)
    grouped = {}
    for doc in docs:
        grouped.setdefault(doc.get_category_display(), []).append(doc)
    return render(request, "core/documents.html", {"grouped_documents": grouped})


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
