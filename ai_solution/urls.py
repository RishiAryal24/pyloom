from django.contrib import admin
from django.urls import path, include, re_path
from core import views  # Import views from the correct app
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('django-admin/', admin.site.urls),  # Custom admin URL (if necessary)
    path('admin/', include('admin_dashboard.urls')),  # Custom admin URLs
    path('', views.home, name='home'),  # Home page URL for 'Back to site'
    path('admin/password-reset/', views.password_reset_request, name='admin_password_reset'),
    path('tinymce/', include('tinymce.urls')),  # TinyMCE URLs for rich text editing
    path('', include('core.urls')),  # Include core app URLs
    path('api/', include('core.api.urls')),
]

# Uploaded media handling.
#
# cPanel/Passenger routes /media/ through Django before LiteSpeed can serve the
# public_html/media symlink, and django.conf.urls.static.static() is debug-only.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
