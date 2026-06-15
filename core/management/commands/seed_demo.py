"""Set up the site's real foundational content for Foundation for Human Care.

This is a NEW organisation, so we do NOT seed any fake achievements, statistics,
news stories, past events, photos, or donations. We only set up:
  - the organisation's identity / mission (Site Settings)
  - the real causes the foundation will run (Programs)
  - the genuine ways people can help (Volunteer opportunities)

It also clears any previously-seeded placeholder content (blog posts, events,
gallery albums) so nothing dummy is shown.

Usage:  python manage.py seed_demo   (safe to re-run)
"""
from django.core.management.base import BaseCommand

from blog.models import Category, Post
from core.models import SiteSetting
from events.models import Event
from gallery.models import Album
from programs.models import Program
from volunteers.models import Opportunity


class Command(BaseCommand):
    help = "Set up real foundational content for Foundation for Human Care."

    def handle(self, *args, **options):
        self.stdout.write("Setting up foundational content...")

        # --- Remove any previously-seeded placeholder / dummy content ---
        Post.objects.all().delete()
        Category.objects.all().delete()
        Event.objects.all().delete()
        Album.objects.all().delete()

        # --- Organisation identity & mission (no fake stats) ---
        org = SiteSetting.load()
        org.org_name = "Foundation for Human Care"
        org.tagline = "Food, healthcare and shelter for the poor, the elderly and orphaned children"
        org.about_short = (
            "Foundation for Human Care is a newly founded non-profit working across "
            "Andhra Pradesh and Telangana to care for the people society too often "
            "leaves behind — the poor, the destitute elderly, and children without parents."
        )
        org.about_long = (
            "Foundation for Human Care has just been started with one purpose: to make "
            "sure no one in our communities goes without food, medical care, or a safe "
            "place to belong.\n\n"
            "We are focusing our work in Andhra Pradesh and Telangana, beginning with "
            "three groups in greatest need — poor families who cannot afford healthcare, "
            "elderly people who have been left without family or support, and children "
            "who have lost their parents.\n\n"
            "We are at the very beginning of this journey. Every donation, every "
            "volunteer, and every helping hand will directly shape the lives we are able "
            "to reach. We would be honoured to have you with us from the start."
        )
        org.mission = (
            "To provide food, healthcare and shelter to the poor, the destitute elderly, "
            "and orphaned children across Andhra Pradesh and Telangana."
        )
        org.vision = (
            "A society where no person — young or old — is left without food, care, "
            "or dignity."
        )
        org.hero_title = "Care for those who need it most"
        org.hero_subtitle = (
            "Food, healthcare and shelter for the poor, the elderly and children "
            "without parents — across Andhra Pradesh & Telangana."
        )
        # Region only; leave email/phone/bank blank for you to fill with real details.
        org.address = "Andhra Pradesh & Telangana, India"
        org.email = ""
        org.phone = ""
        org.bank_details = ""
        # Brand-new org: no impact numbers yet.
        org.stat_people_helped = 0
        org.stat_volunteers = 0
        org.stat_projects = 0
        org.stat_funds_raised = 0
        org.save()

        # --- Real causes (programs) — nothing raised yet, honest goals ---
        programs = [
            (
                "Food for the Hungry",
                "Daily meals for the homeless, destitute elderly and poor families.",
                "No one should go to bed hungry. Through this program we aim to provide "
                "nutritious daily meals to homeless people, elderly citizens with no "
                "family to care for them, and families who cannot afford enough food. "
                "Your support helps us start and sustain community kitchens and meal "
                "drives across Andhra Pradesh and Telangana.",
                300000,
            ),
            (
                "Healthcare for the Needy",
                "Medicines, check-ups and treatment for those who can't afford care.",
                "Many poor and elderly people go without treatment simply because they "
                "cannot afford a doctor or medicines. This program will fund free health "
                "check-ups, essential medicines, and medical support for the poor and "
                "the elderly in our communities.",
                500000,
            ),
            (
                "Care for Orphan Children",
                "Shelter, food, education and love for children without parents.",
                "Children who have lost their parents need more than shelter — they need "
                "food, education, healthcare, and people who care. This program is "
                "dedicated to giving orphaned and abandoned children a safe home and a "
                "real chance at a good life.",
                700000,
            ),
            (
                "Support for the Elderly",
                "Care and dignity for elderly people left without family.",
                "Too many elderly people are left alone, without family or means to look "
                "after themselves. Through this program we aim to provide food, "
                "healthcare, companionship and shelter so that our elders can live the "
                "rest of their lives with dignity.",
                400000,
            ),
        ]
        for title, summary, body, goal in programs:
            Program.objects.update_or_create(
                title=title,
                defaults=dict(
                    summary=summary,
                    body=body,
                    goal_amount=goal,
                    raised_amount=0,          # nothing raised yet — honest
                    is_featured=True,
                    is_published=True,
                ),
            )
        # Remove any old placeholder programs that aren't part of the real set.
        real_titles = [p[0] for p in programs]
        Program.objects.exclude(title__in=real_titles).delete()

        # --- Genuine ways people can help (volunteer asks, not claims) ---
        opportunities = [
            (
                "Food Distribution Volunteer",
                "Help prepare and distribute meals to the homeless, elderly and poor "
                "families in your area.",
                "Andhra Pradesh / Telangana",
                "Compassion, Teamwork",
            ),
            (
                "Elderly Care Volunteer",
                "Spend time with and care for elderly people who have no family to "
                "support them.",
                "Andhra Pradesh / Telangana",
                "Patience, Compassion",
            ),
            (
                "Volunteer for Children",
                "Mentor, teach and care for orphaned and abandoned children.",
                "Andhra Pradesh / Telangana",
                "Teaching, Patience, Care",
            ),
        ]
        for title, desc, loc, skills in opportunities:
            Opportunity.objects.update_or_create(
                title=title,
                defaults=dict(
                    description=desc, location=loc, skills=skills,
                    openings=1, is_open=True,
                ),
            )
        real_op_titles = [o[0] for o in opportunities]
        Opportunity.objects.exclude(title__in=real_op_titles).delete()

        self.stdout.write(self.style.SUCCESS("Foundational content is set up."))
        self.stdout.write(
            "Next: add your real contact details, bank/UPI info, logo and photos "
            "from the admin at /admin/."
        )
