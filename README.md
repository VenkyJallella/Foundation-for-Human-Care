# Foundation for Human Care — NGO Website

A complete Django website for the **Foundation for Human Care** NGO, with a public
site, a logged-in **user portal**, and a themed **admin portal**.

## Features

**Public site**
- Home page with hero, impact stats, featured programs, and latest news
- About, Contact (saves messages), Newsletter signup
- **Programs / causes** with fundraising progress bars
- **Photo gallery** (albums → photos with lightbox)
- **Blog / news** with categories and pagination
- **Events** (upcoming/past) with online registration
- **Volunteer** opportunities with application forms
- **Donations** via **Razorpay** (UPI / cards / netbanking) with printable receipts

**User portal** (`/accounts/dashboard/`, login required)
- Dashboard overview (total donated, applications, registrations)
- My Donations + downloadable receipts
- My Volunteering (application status)
- My Events (registrations)
- Edit profile (info + photo), password reset

**Admin portal** (`/admin/`)
- Themed with django-jazzmin, branded for FHC
- Manage all content: programs, gallery, blog, events, volunteers, donations,
  site settings, newsletter subscribers, contact messages

## Tech stack
Django 5 · Django templates + Bootstrap 5 · django-crispy-forms · Pillow ·
Razorpay · django-jazzmin · django-environ · WhiteNoise · SQLite (dev).

## Setup

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env        # Windows  (cp .env.example .env on macOS/Linux)
#   then edit .env — at minimum keep DEBUG=True for local development

# 4. Set up the database
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. (Optional) Load demo content so the site looks populated
python manage.py seed_demo

# 7. Run
python manage.py runserver
```

Visit:
- Public site: http://127.0.0.1:8000/
- User dashboard: http://127.0.0.1:8000/accounts/dashboard/
- Admin portal: http://127.0.0.1:8000/admin/

## Enabling live donations (Razorpay)

The donation flow works out of the box in **pledge mode** (records the donation
and shows bank/UPI details). To accept live online payments:

1. Create a free account at https://dashboard.razorpay.com and get your **API keys**
   (use **Test Mode** keys first).
2. Put them in `.env`:
   ```
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxx
   ```
3. Restart the server. The Donate page now opens Razorpay Checkout. Payment
   signatures are verified server-side before a donation is marked **Paid**.
4. (Optional) Set up a webhook in the Razorpay dashboard pointing to
   `/donate/webhook/` and put the signing secret in `RAZORPAY_WEBHOOK_SECRET`
   for backup reconciliation.

Test card / UPI details for Razorpay test mode are in the
[Razorpay docs](https://razorpay.com/docs/payments/payments/test-card-details/).

## Project layout

| App          | Responsibility |
|--------------|----------------|
| `accounts`   | Custom email-login user, profile, auth, user dashboard |
| `core`       | Home/About/Contact, site settings, newsletter |
| `programs`   | Causes/programs with fundraising goals |
| `gallery`    | Photo albums and photos |
| `blog`       | News posts and categories |
| `events`     | Events and registrations |
| `donations`  | Donations + Razorpay integration + receipts |
| `volunteers` | Volunteer opportunities and applications |

## Editing site content

Most content is editable from the admin without touching code:
- **Site Settings** (single record): org name, tagline, hero banner, impact stats,
  contact info, social links, bank/UPI details.
- Add **Programs**, **Albums + Photos**, **Blog posts**, **Events**, and
  **Volunteer opportunities** from their admin sections.

## Going to production (checklist)

- Set `DEBUG=False`, a strong `SECRET_KEY`, and real `ALLOWED_HOSTS` in `.env`
- Switch to PostgreSQL (update `DATABASES` in `fhc/settings.py`)
- Run `python manage.py collectstatic`
- Serve behind HTTPS; configure real SMTP email settings
- Use live Razorpay keys
