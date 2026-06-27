import os
import sys
from pathlib import Path
import django
from datetime import date, time

# Ensure project root is on sys.path so Django settings package can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_solution.settings')
django.setup()

from core.models import Training

training_data = {
    'summary': 'A practical, hands-on workshop on applying AI to real business problems.',
    'course_overview': '<p>This workshop covers data preparation, model selection, deployment, and monitoring.</p>',
    'duration': '2 days',
    'who_can_attend': 'Developers, Data Scientists, Technical Managers',
    'prerequisites': 'Basic Python and familiarity with machine learning concepts',
    'location': 'Online',
    'date': date(2026, 8, 1),
    'time': time(9, 0),
    'price': 'Free',
    'registration_url': 'https://example.com/register',
    'status': 'upcoming',
    'is_featured': True,
}

title = 'Intro to Applied AI: Practical Workshops'

training, created = Training.objects.get_or_create(title=title, defaults=training_data)
if created:
    print('Created Training:', training.id, training.title, training.slug)
else:
    print('Training already exists:', training.id, training.title, training.slug)

print('Total trainings:', Training.objects.count())
