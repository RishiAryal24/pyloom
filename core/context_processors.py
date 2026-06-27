from .models import SiteSettings, ContactInquiry, Feedback, Solution, Service, Training

def site_settings(request):
    """Add site settings to all templates"""
    settings_obj = SiteSettings.load()
    if settings_obj:
        return {'settings': settings_obj}

    # Provide safe defaults when no SiteSettings instance exists to avoid template errors
    return {
        'settings': {
            'site_name': 'PyLoom',
            'slogan': 'Weaving Innovation Beyond Expectations',
            'contact_email': 'info@pyloomtech.com',
            'contact_phone': '',
            'logo': None,
            'favicon': None,
        }
    }


def navigation_items(request):
    """Add dynamic navigation items for services and trainings."""
    nav_services = Service.objects.filter(is_active=True).order_by('order', 'title')[:10]
    nav_trainings = Training.objects.filter(status='upcoming').order_by('date', 'time')[:10]

    return {
        'nav_services': nav_services,
        'nav_trainings': nav_trainings,
    }


def admin_notifications(request):
    """Add admin notifications to templates"""
    if request.user.is_authenticated and hasattr(request.user, 'has_admin_access') and request.user.has_admin_access():
        return {
            'stats': {
                'unread_inquiries': ContactInquiry.objects.filter(is_read=False).count(),
                'pending_feedback': Feedback.objects.filter(is_approved=False).count(),
            }
        }
    return {}