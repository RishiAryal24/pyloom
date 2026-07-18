#!/usr/bin/env python
import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ai_solution.settings'
django.setup()

from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()
c = Client(enforce_csrf_checks=False)
try:
    response = c.get('/', SERVER_NAME='localhost')
    print(f'Status: {response.status_code}')
    if response.status_code >= 400:
        print('Response:')
        content = response.content.decode('utf-8')
        # Find the actual error message
        if 'Traceback' in content:
            start = content.find('Traceback')
            end = content.find('</pre>', start)
            if end > 0:
                error_text = content[start:end]
                # Remove HTML tags
                error_text = error_text.replace('<pre', '').replace('</pre>', '')
                error_text = error_text.replace('&lt;', '<').replace('&gt;', '>')
                print(error_text[:2000])
        else:
            print(content[:1000])
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
