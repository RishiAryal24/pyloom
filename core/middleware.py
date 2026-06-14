from django.shortcuts import render
from django.urls import reverse
from core.models import SiteSettings


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is enabled
        try:
            site_settings = SiteSettings.load()
            maintenance_mode = site_settings.maintenance_mode if site_settings else False
        except:
            maintenance_mode = False

        # Allow access to admin and login URLs even in maintenance mode
        allowed_paths = [
            reverse('admin_login'),
            reverse('admin_dashboard'),
            reverse('admin:index'),
            reverse('admin:logout'),
            '/admin/',
        ]

        # Check if user is authenticated and has admin access
        user_has_access = request.user.is_authenticated and (
            request.user.is_superuser or request.user.has_admin_access()
        )

        # If maintenance mode is on and user doesn't have access, show maintenance page
        if maintenance_mode and not user_has_access:
            # Check if current path is in allowed paths
            path_allowed = any(request.path.startswith(path) for path in allowed_paths)
            
            if not path_allowed:
                return render(request, 'maintenance.html', status=503)

        response = self.get_response(request)
        return response
