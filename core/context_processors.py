from types import SimpleNamespace

from .models import SiteSettings, ContactInquiry, Feedback


DEFAULT_SITE_SETTINGS = SimpleNamespace(
    site_name='PyLoom',
    slogan='Weaving Innovation Beyond Expectations',
    logo=None,
    favicon=None,
    contact_email='',
    contact_phone='',
    address='',
    facebook_url='',
    twitter_url='',
    linkedin_url='',
    instagram_url='',
    youtube_url='',
    maintenance_mode=False,
)

def site_settings(request):
    """Add site settings to all templates"""
    return {
        'settings': SiteSettings.load() or DEFAULT_SITE_SETTINGS
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
