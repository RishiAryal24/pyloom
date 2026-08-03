import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_solution.settings')
sys.path.insert(0, os.getcwd())
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
    },
)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.email = email
user.set_password(password)
user.save()

print('created' if created else 'updated')
print('username:', user.username)
print('password:', password)
print('email:', user.email)
