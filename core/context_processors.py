from .models import SiteSettings, ContactInquiry, Feedback, Solution, Service, Training
import json

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


def schema_org_data(request):
    """Generate dynamic Schema.org JSON-LD structured data for SEO"""
    settings_obj = SiteSettings.load()
    
    if not settings_obj:
        settings_obj = SiteSettings.objects.first()
    
    if settings_obj:
        logo_url = settings_obj.logo.url if settings_obj.logo else 'https://www.pyloomtech.com/static/core/img/pyloom-logo.png'
        address_parts = settings_obj.address.replace('<p>', '').replace('</p>', '').split(',') if settings_obj.address else []
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": settings_obj.site_name or "PyLoom",
            "url": "https://www.pyloomtech.com",
            "logo": logo_url,
            "description": "Advanced AI-powered technology solutions for modern businesses",
            "sameAs": [url for url in [
                settings_obj.linkedin_url,
                settings_obj.twitter_url,
                settings_obj.facebook_url,
                settings_obj.instagram_url,
                settings_obj.youtube_url,
            ] if url],
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "Customer Service",
                "email": settings_obj.contact_email or "contact@pyloomtech.com",
            }
        }
        
        # Add phone if available
        if settings_obj.contact_phone:
            schema_data["contactPoint"]["telephone"] = settings_obj.contact_phone
        
        # Add address if available
        if settings_obj.address:
            schema_data["address"] = {
                "@type": "PostalAddress",
                "streetAddress": settings_obj.address.replace('<p>', '').replace('</p>', '').strip(),
                "addressCountry": "US"
            }
        
        return {'schema_org_json': json.dumps(schema_data, ensure_ascii=False)}
    
    return {'schema_org_json': '{}'}
