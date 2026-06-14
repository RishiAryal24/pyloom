# cPanel Deployment for pyloomtech.com

Use cPanel's **Setup Python App** for this project. The old static-file copy flow is not enough because this is a Django application.

After the first Python App setup, Git deployment can run automatically through `.cpanel.yml`. It calls `scripts/deploy_cpanel.sh`, which installs dependencies, runs migrations, collects static files, and restarts Passenger.

## Python App

- Application root: the folder containing `manage.py`
- Application startup file: `passenger_wsgi.py`
- Application entry point: `application`
- Application URL: `pyloomtech.com`

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

## Manual First-Time Commands

If you need to run the steps manually, use:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Restart the Python app after changes. The `.cpanel.yml` file also touches `tmp/restart.txt` during Git deployment so Passenger reloads the app.

## URLs

- Public site: `https://pyloomtech.com/`
- Custom dashboard: `https://pyloomtech.com/admin/`
- Django admin: `https://pyloomtech.com/django-admin/`
