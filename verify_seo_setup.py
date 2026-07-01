#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_solution.settings')
django.setup()

from django.template.loader import get_template
from core.models import SiteSettings

print("=" * 60)
print("SEO SETUP VERIFICATION")
print("=" * 60)

# Test 1: Template loading
try:
    t = get_template('base.html')
    print("✓ Template 'base.html' loads successfully")
except Exception as e:
    print(f"✗ Template error: {e}")

# Test 2: Site settings
try:
    s = SiteSettings.load()
    if s:
        print(f"✓ Site Settings loaded successfully")
        print(f"  - Site Name: {s.site_name}")
        print(f"  - Contact Email: {s.contact_email}")
        print(f"  - Contact Phone: {s.contact_phone}")
    else:
        print("⚠ No site settings found - run: python manage.py init_site_settings")
except Exception as e:
    print(f"✗ Site settings error: {e}")

# Test 3: Sitemaps check
try:
    from core.sitemaps import ArticleSitemap, SolutionSitemap
    print("✓ Sitemaps configured successfully")
except Exception as e:
    print(f"✗ Sitemaps error: {e}")

# Test 4: Context processor
try:
    from core.context_processors import schema_org_data
    print("✓ Schema.org context processor loaded")
except Exception as e:
    print(f"✗ Context processor error: {e}")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Update site settings in Django admin")
print("2. Submit sitemaps to Google Search Console")
print("3. Test schema with: https://search.google.com/test/rich-results")
print("=" * 60)
