# cPanel Deployment for pyloomtech.com

Use cPanel's **Setup Python App** for this project. The old static-file copy flow is not enough because this is a Django application.

After the first Python App setup, Git deployment can run automatically through `.cpanel.yml`. It calls `scripts/deploy_cpanel.sh`, which:

- locates the cPanel virtualenv, including CloudLinux's symlinked Python wrapper;
- installs dependencies and validates `passenger_wsgi.py`;
- runs Django checks, migrations, and `collectstatic`;
- creates `~/public_html/static` and `~/public_html/media` symlinks so LiteSpeed serves assets directly;
- restarts Passenger and verifies `https://pyloomtech.com/health/`.

## Python App

- Application root: the folder containing `manage.py`
- Application startup file: `passenger_wsgi.py`
- Application entry point: `application`
- Application URL: `pyloomtech.com`
- Python version: use Python 3.10 or newer. Do not use system Python 3.6; Django 5 will not run there.

## Environment Variables

Set these in cPanel's Python app environment:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=pyloomtech.com,www.pyloomtech.com
CSRF_TRUSTED_ORIGINS=https://pyloomtech.com,https://www.pyloomtech.com

DB_NAME=your_cpanel_mysql_database
DB_USER=your_cpanel_mysql_user
DB_PASSWORD=your_cpanel_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

Add email settings too if contact/password-reset email should work.

## Automatic Git Deployment

On every cPanel Git deployment, `.cpanel.yml` runs:

```bash
/bin/bash scripts/deploy_cpanel.sh
```

The script tries to find the active cPanel virtualenv automatically. If cPanel has not created the Python App yet, the script will stop and ask you to create it first.

The deployment intentionally refuses to replace an existing non-symlink
`public_html/static` or `public_html/media` path. Move that old path manually,
then redeploy. To use another document root, set `PUBLIC_ROOT`. To use another
health URL, set `DEPLOY_HEALTH_URL`. Emergency-only HTTP check bypass:
`SKIP_HTTP_HEALTHCHECK=1`.

## Manual First-Time Commands

If you need to run the steps manually, use:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Restart the Python app after changes. The `.cpanel.yml` file also touches `tmp/restart.txt` during Git deployment so Passenger reloads the app.

## Verification

```bash
curl -I https://pyloomtech.com/
curl https://pyloomtech.com/health/
curl -o /dev/null -s \
  -w "Static TTFB: %{time_starttransfer}s Total: %{time_total}s\n" \
  https://pyloomtech.com/static/core/css/main.css
```

The health endpoint should return:

```json
{"status": "ok"}
```

## Optimize Uploaded Images

Large uploaded PNG/JPEG files make the public pages feel slow even when Django
and LiteSpeed are healthy. Preview potential savings first:

```bash
python manage.py optimize_media_images
```

Apply safe in-place resizing and compression while keeping the same media URLs:

```bash
python manage.py optimize_media_images --apply
```

The defaults cap images at `1600x1200`. Custom example:

```bash
python manage.py optimize_media_images --apply --max-width 1400 --max-height 1000 --quality 80
```

## URLs

- Public site: `https://pyloomtech.com/`
- Custom dashboard: `https://pyloomtech.com/admin/`
- Django admin: `https://pyloomtech.com/django-admin/`
