# PyLoom

A modern, responsive Django-powered website for PyLoom.

## Features

- Custom admin dashboard with improved UI/UX
- Content management for articles, events, projects, solutions, and more
- Contact form with inquiry management
- User authentication and role-based access
- Maintenance mode support
- Responsive design for all devices

## Prerequisites

- Python 3.8 or higher
- pip
- Virtual environment (recommended)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "e:\Projects\pyloom website\pyloom"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional):**
   - Create a `.env` file in the project root
   - Add your configuration (database settings, secret key, etc.)

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (to access admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files (for production):**
   ```bash
   python manage.py collectstatic
   ```

## Running the Development Server

```bash
python manage.py runserver
```

Then open your browser and navigate to:
- Frontend: http://127.0.0.1:8000/
- Custom Admin Dashboard: http://127.0.0.1:8000/admin/
- Django Admin: http://127.0.0.1:8000/django-admin/

## Project Structure

```
pyloom/
├── admin_dashboard/    # Custom admin views and templates
├── core/               # Main Django app with models, views, forms
├── templates/          # HTML templates
├── static/             # Static files (CSS, JS, images)
├── media/              # User-uploaded media files (gitignored)
├── ai_solution/        # Project settings and URLs
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Default Admin Credentials

If you used the superuser creation script:
- Username: `pyadmin`
- Password: `PyAdmin123!`

**Important:** Change these credentials in production!

## Tech Stack

- **Backend:** Django 5.0
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Database:** MySQL (with SQLite fallback)
- **Other:** Django REST Framework, TinyMCE, django-crispy-forms

## Deployment

Before deploying, make sure to:
1. Set `DEBUG = False` in `settings.py`
2. Configure your production database
3. Set a secure `SECRET_KEY`
4. Configure allowed hosts
5. Set up static files serving (e.g., with Whitenoise or a CDN)
