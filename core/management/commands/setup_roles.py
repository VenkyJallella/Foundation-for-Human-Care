"""Create staff permission groups for delegating admin access safely.

Usage:  python manage.py setup_roles   (safe to re-run)

After running, assign a user to a group in the admin (Users -> pick user ->
tick "Staff status" and add the group). They then get only that group's access.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Category, Post
from core.models import ContactMessage, Document, NewsletterSubscriber
from donations.models import Donation
from events.models import Event, EventRegistration
from gallery.models import Album, Photo
from programs.models import Program
from volunteers.models import Application, Opportunity

ALL = ("add", "change", "delete", "view")

# group name -> list of (model, allowed actions)
ROLES = {
    "Content Editors": [
        (Post, ALL), (Category, ALL), (Album, ALL), (Photo, ALL),
        (Program, ALL), (Event, ALL), (Document, ALL),
        (EventRegistration, ("view",)),
    ],
    "Volunteer Coordinators": [
        (Opportunity, ALL),
        (Application, ("view", "change")),
        (EventRegistration, ("view",)),
    ],
    "Supporters & Donations (read-only)": [
        (Donation, ("view",)),
        (Application, ("view",)),
        (EventRegistration, ("view",)),
        (ContactMessage, ("view", "change")),
        (NewsletterSubscriber, ("view",)),
    ],
}


class Command(BaseCommand):
    help = "Create staff permission groups (Content Editors, etc.)."

    def handle(self, *args, **options):
        for group_name, model_perms in ROLES.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            perms = []
            for model, actions in model_perms:
                ct = ContentType.objects.get_for_model(model)
                for action in actions:
                    codename = f"{action}_{model._meta.model_name}"
                    try:
                        perms.append(Permission.objects.get(content_type=ct, codename=codename))
                    except Permission.DoesNotExist:
                        self.stderr.write(f"  (skipped missing permission {codename})")
            group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(f"{group_name}: {len(perms)} permissions set"))

        self.stdout.write(
            "\nDone. In the admin, edit a user, tick 'Staff status', and add them to a "
            "group to grant that role."
        )
