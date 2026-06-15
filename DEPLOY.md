# Deploying to a Hostinger VPS (domain: affinix.cloud)

This guide deploys the site to an Ubuntu VPS using **Nginx + Gunicorn**, with a
free **Let's Encrypt SSL** certificate. It assumes a fresh Ubuntu 22.04/24.04 VPS.

> You can use the root domain `affinix.cloud` or a subdomain like
> `fhc.affinix.cloud`. Just use the same name consistently everywhere below.

---

## Step 1 — Point the domain to your VPS

1. Find your VPS **IP address** in the Hostinger hPanel (VPS → Overview).
2. In Hostinger **DNS settings** for `affinix.cloud`, add/edit **A records**:
   - `@`  →  `YOUR_VPS_IP`
   - `www` →  `YOUR_VPS_IP`
   - (or `fhc` → `YOUR_VPS_IP` if using a subdomain)
3. DNS can take a few minutes to a couple of hours to propagate.

---

## Step 2 — Connect to the VPS and install packages

```bash
ssh root@YOUR_VPS_IP

apt update && apt upgrade -y
apt install -y python3-venv python3-pip nginx git
```

---

## Step 3 — Put the code on the server

The project folder goes in `/var/www/fhc`.

**Option A — via Git (recommended).** Push your project to GitHub/GitLab, then:
```bash
git clone YOUR_REPO_URL /var/www/fhc
```

**Option B — upload directly.** Use an SFTP client (e.g. FileZilla) to upload the
project folder to `/var/www/fhc`. Skip the `.venv`, `__pycache__`, and
`staticfiles` folders.

### Bring your existing content with you
Your blog post, gallery album, founder info, and programs live in **`db.sqlite3`**,
and your uploaded photos live in **`media/`**. These are NOT in Git (they're
git-ignored), so upload them separately via SFTP to keep your content:
- Local `db.sqlite3`  →  `/var/www/fhc/db.sqlite3`
- Local `media/` folder  →  `/var/www/fhc/media/`

(If you skip this, you'll start with an empty site and can re-add content in the admin.)

---

## Step 4 — Set up the Python environment

```bash
cd /var/www/fhc
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

---

## Step 5 — Create the production `.env`

```bash
cp deploy/.env.production.example .env
nano .env
```
Fill it in. Generate a secret key with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```
Set at least: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (your domain + IP),
`CSRF_TRUSTED_ORIGINS`, and leave `SECURE_SSL_REDIRECT=False` for now.

---

## Step 6 — Migrate, collect static, create admin

```bash
cd /var/www/fhc
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput

# Only if you did NOT upload db.sqlite3 (i.e. starting fresh):
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py seed_demo
```

Give the web server ownership of the files (needed for uploads + the database):
```bash
chown -R www-data:www-data /var/www/fhc
```

---

## Step 7 — Run the app with Gunicorn (systemd)

```bash
cp /var/www/fhc/deploy/gunicorn-fhc.service /etc/systemd/system/gunicorn-fhc.service
systemctl daemon-reload
systemctl enable --now gunicorn-fhc
systemctl status gunicorn-fhc      # should show "active (running)"
```

---

## Step 8 — Put Nginx in front

```bash
cp /var/www/fhc/deploy/nginx-fhc.conf /etc/nginx/sites-available/fhc
# edit the file if your domain differs:
nano /etc/nginx/sites-available/fhc

ln -s /etc/nginx/sites-available/fhc /etc/nginx/sites-enabled/fhc
rm -f /etc/nginx/sites-enabled/default      # remove the default placeholder site
nginx -t                                    # test config
systemctl restart nginx
```

Now visit **http://affinix.cloud** — the site should load (without HTTPS yet).

---

## Step 9 — Enable HTTPS (free SSL)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d affinix.cloud -d www.affinix.cloud
```
Follow the prompts (enter an email, agree to terms). Certbot installs the
certificate and sets up the HTTP→HTTPS redirect automatically.

Then turn on Django's HTTPS enforcement:
```bash
nano /var/www/fhc/.env      # set SECURE_SSL_REDIRECT=True
systemctl restart gunicorn-fhc
```

Your site is now live at **https://affinix.cloud** 🎉

---

## Updating the site later (after code changes)

```bash
cd /var/www/fhc
git pull                                   # or re-upload changed files
.venv/bin/pip install -r requirements.txt  # if dependencies changed
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /var/www/fhc
systemctl restart gunicorn-fhc
```

---

## Switching to your real domain later

When you buy your permanent domain:
1. Point its DNS A records to the same VPS IP.
2. Add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `.env`.
3. Update `server_name` in `/etc/nginx/sites-available/fhc`.
4. Run `certbot --nginx -d newdomain.com -d www.newdomain.com`.
5. `systemctl restart gunicorn-fhc && systemctl restart nginx`.

---

## Troubleshooting

- **502 Bad Gateway** → Gunicorn isn't running. Check `systemctl status gunicorn-fhc`
  and `journalctl -u gunicorn-fhc -n 50`.
- **400 Bad Request** → your domain isn't in `ALLOWED_HOSTS`. Fix `.env`, restart Gunicorn.
- **CSRF error on forms** → add `https://yourdomain` to `CSRF_TRUSTED_ORIGINS`, restart.
- **Static files / CSS missing** → run `collectstatic`, check the `/static/` alias path in Nginx.
- **Redirect loop** → you set `SECURE_SSL_REDIRECT=True` before SSL was ready. Set it
  back to `False` until Certbot is done.
- **Can't upload photos** → ensure `chown -R www-data:www-data /var/www/fhc` was run.

> Note: SQLite is fine for a small site. If traffic grows, switch to PostgreSQL
> by updating the `DATABASES` setting in `fhc/settings.py`.
