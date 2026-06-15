# Deploying to a Hostinger VPS (PostgreSQL + Nginx + Gunicorn)

This deploys the site to an Ubuntu VPS with **PostgreSQL**, **Gunicorn**, **Nginx**,
and free **Let's Encrypt SSL**, and brings across **all your existing content and
photos** from local development.

> Domain: you can use `affinix.cloud` or a subdomain like `fhc.affinix.cloud` —
> just use the same name consistently. Everything here is free beyond the VPS.

---

## Step 0 — On your LOCAL machine: export your data

Your content (blog post, gallery album, founder info, programs, admin user) is in
your local database, and your photos are in the `media/` folder. Export the data:

```powershell
cd "d:\projects\Foundation for Human Care"
.venv\Scripts\python manage.py dumpdata --natural-foreign --natural-primary `
  --exclude contenttypes --exclude auth.permission `
  --exclude admin.logentry --exclude sessions `
  --indent 2 -o data.json
```

This creates **`data.json`**. You'll upload it (and the `media/` folder) to the
server in Step 7. Keep `data.json` private — it contains your admin password hash.

---

## Step 1 — Point the domain to your VPS

1. Get your VPS **IP address** from Hostinger hPanel (VPS → Overview).
2. In Hostinger **DNS** for `affinix.cloud`, add **A records**:
   - `@` → `YOUR_VPS_IP`
   - `www` → `YOUR_VPS_IP`
3. Wait a few minutes for DNS to propagate.

---

## Step 2 — Connect and install packages

```bash
ssh root@YOUR_VPS_IP

apt update && apt upgrade -y
apt install -y python3-venv python3-pip nginx git \
               postgresql postgresql-contrib libpq-dev
```

---

## Step 3 — Create the PostgreSQL database

```bash
sudo -u postgres psql
```
Inside the `psql` prompt (replace `STRONG_DB_PASSWORD` with a real password):
```sql
CREATE DATABASE fhc;
CREATE USER fhcuser WITH PASSWORD 'STRONG_DB_PASSWORD';
ALTER ROLE fhcuser SET client_encoding TO 'utf8';
ALTER ROLE fhcuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE fhcuser SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE fhc TO fhcuser;
\c fhc
GRANT ALL ON SCHEMA public TO fhcuser;
\q
```

Your `DATABASE_URL` will be:
`postgres://fhcuser:STRONG_DB_PASSWORD@localhost:5432/fhc`

---

## Step 4 — Get the code on the server

```bash
git clone https://github.com/VenkyJallella/Foundation-for-Human-Care.git /var/www/fhc
cd /var/www/fhc
```

---

## Step 5 — Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

---

## Step 6 — Create the production `.env`

```bash
cp deploy/.env.production.example .env
nano .env
```
Fill in:
- `SECRET_KEY` → generate one: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DEBUG=False`
- `ALLOWED_HOSTS=affinix.cloud,www.affinix.cloud,YOUR_VPS_IP`
- `CSRF_TRUSTED_ORIGINS=https://affinix.cloud,https://www.affinix.cloud`
- `SECURE_SSL_REDIRECT=False`  (turn on later, Step 10)
- `DATABASE_URL=postgres://fhcuser:STRONG_DB_PASSWORD@localhost:5432/fhc`
- Email + Razorpay values as needed.

---

## Step 7 — Create the schema and import your content + photos

Create the database tables:
```bash
.venv/bin/python manage.py migrate
```

Upload your local **`data.json`** and **`media/`** folder to the server using an
SFTP client (FileZilla) or `scp` from your local machine:
```powershell
# run these from your LOCAL machine
scp data.json root@YOUR_VPS_IP:/var/www/fhc/data.json
scp -r media root@YOUR_VPS_IP:/var/www/fhc/
```

Back on the server, import the data and collect static files:
```bash
cd /var/www/fhc
.venv/bin/python manage.py loaddata data.json
.venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /var/www/fhc
```

> Your admin login is the same as local (e.g. `admin@fhc.org`). **Change the
> admin password** after going live: log into `/admin/` → top-right → change password.
>
> Starting completely fresh instead? Skip `loaddata` and run
> `createsuperuser` + `seed_demo` instead.

---

## Step 8 — Run the app with Gunicorn

```bash
cp /var/www/fhc/deploy/gunicorn-fhc.service /etc/systemd/system/gunicorn-fhc.service
systemctl daemon-reload
systemctl enable --now gunicorn-fhc
systemctl status gunicorn-fhc      # should be "active (running)"
```

---

## Step 9 — Nginx

```bash
cp /var/www/fhc/deploy/nginx-fhc.conf /etc/nginx/sites-available/fhc
nano /etc/nginx/sites-available/fhc      # edit domain if needed
ln -s /etc/nginx/sites-available/fhc /etc/nginx/sites-enabled/fhc
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```
Visit **http://affinix.cloud** — the site should load (no HTTPS yet).

---

## Step 10 — Enable HTTPS (free SSL)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d affinix.cloud -d www.affinix.cloud
```
Then enforce HTTPS in Django:
```bash
nano /var/www/fhc/.env      # set SECURE_SSL_REDIRECT=True
systemctl restart gunicorn-fhc
```

🎉 Live at **https://affinix.cloud**

---

## Updating after code changes

```bash
cd /var/www/fhc
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /var/www/fhc
systemctl restart gunicorn-fhc
```

> After the first import, **don't** run `loaddata` again — content now lives in
> the production database and is edited through the admin.

---

## Switching to your real domain later

1. Point its DNS A records to the same VPS IP.
2. Add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `.env`.
3. Update `server_name` in `/etc/nginx/sites-available/fhc`.
4. `certbot --nginx -d newdomain.com -d www.newdomain.com`
5. `systemctl restart gunicorn-fhc && systemctl restart nginx`

---

## Backups (recommended)

- **Database:** `sudo -u postgres pg_dump fhc > fhc-backup-$(date +%F).sql`
- **Photos:** back up the `/var/www/fhc/media/` folder.
- Automate with a weekly cron job once you're settled.

---

## Troubleshooting

- **502 Bad Gateway** → Gunicorn down. `systemctl status gunicorn-fhc` and
  `journalctl -u gunicorn-fhc -n 50`.
- **400 Bad Request** → domain missing from `ALLOWED_HOSTS`. Fix `.env`, restart Gunicorn.
- **CSRF error on forms** → add `https://yourdomain` to `CSRF_TRUSTED_ORIGINS`, restart.
- **CSS/images missing** → re-run `collectstatic`; check `/static/` & `/media/` paths in Nginx.
- **Redirect loop** → `SECURE_SSL_REDIRECT=True` set before SSL was ready. Set `False` until Certbot done.
- **Can't upload photos** → run `chown -R www-data:www-data /var/www/fhc`.
- **DB connection refused** → check `DATABASE_URL` password and that `postgresql` is running
  (`systemctl status postgresql`).
