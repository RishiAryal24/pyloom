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
    'learning_outcomes': '<ul><li>Understand AI and Generative AI concepts</li><li>Use ChatGPT and other assistants effectively</li><li>Write powerful prompts</li><li>Create emails, reports and presentations with AI</li><li>Automate repetitive office tasks</li></ul>',
    'duration': '15 Days (30 Hours)',
    'delivery_mode': 'Live Online Instructor-Led Training',
    'class_schedule': '2 Hours per Day',
    'level': 'beginner',
    'who_can_attend': 'Corporate Employees; Managers; HR; Finance; Sales; Marketing; Customer Support; Business Analysts; Project Managers; Entrepreneurs; Fresh Graduates',
    'prerequisites': 'Basic computer knowledge. No programming or AI experience required.',
    'certificate': 'Certificate of Completion from PyLoom Technologies',
    'location': 'Online',
    'date': date(2026, 8, 1),
    'date': date(2026, 8, 1),
    'start_date': date(2026, 8, 1),
    'time': time(9, 0),
    'price': 'Free',
    'registration_url': 'https://example.com/register',
    'status': 'upcoming',
    'is_featured': True,
}

title = 'Intro to Applied AI: Practical Workshops'
title = 'AI for Corporate Professionals'

training, created = Training.objects.get_or_create(title=title, defaults=training_data)
if created:
    print('Created Training:', training.id, training.title, training.slug)
else:
    print('Training already exists:', training.id, training.title, training.slug)

print('Total trainings:', Training.objects.count())
