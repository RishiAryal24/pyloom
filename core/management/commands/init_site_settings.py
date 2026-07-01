from django.core.management.base import BaseCommand
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Initialize or update PyLoom site settings with proper contact information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing settings instead of creating new ones'
        )

    def handle(self, *args, **options):
        """Initialize PyLoom site settings"""
        
        try:
            site_settings, created = SiteSettings.objects.get_or_create(pk=1)
            
            # Update with PyLoom branding
            site_settings.site_name = 'PyLoom Technologies'
            site_settings.slogan = 'Weaving Innovation Beyond Expectations'
            site_settings.contact_email = 'info@pyloomtech.com'
            site_settings.contact_phone = '+1 (555) 123-4567'  # Update with actual phone
            site_settings.address = 'PyLoom Technologies<br>Tech City, USA'  # Update with actual address
            
            # Social media URLs - Update with actual URLs
            site_settings.linkedin_url = 'https://www.linkedin.com/company/pyloom'
            site_settings.twitter_url = 'https://twitter.com/pyloomtech'
            site_settings.facebook_url = 'https://facebook.com/pyloomtech'
            site_settings.instagram_url = 'https://instagram.com/pyloomtech'
            site_settings.youtube_url = 'https://youtube.com/@pyloomtech'
            
            site_settings.maintenance_mode = False
            site_settings.save()
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('✓ Created new PyLoom site settings')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ Updated PyLoom site settings')
                )
            
            self.stdout.write(f'Site Name: {site_settings.site_name}')
            self.stdout.write(f'Contact Email: {site_settings.contact_email}')
            self.stdout.write(f'Contact Phone: {site_settings.contact_phone}')
            self.stdout.write(f'Address: {site_settings.address}')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  Important: Update the following details in Django admin:'))
            self.stdout.write('  1. Logo image (admin/site-settings)')
            self.stdout.write('  2. Favicon image (admin/site-settings)')
            self.stdout.write('  3. Actual contact phone number')
            self.stdout.write('  4. Actual company address')
            self.stdout.write('  5. Actual social media URLs')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error initializing site settings: {str(e)}')
            )
