"""
WSGI config for letter_project project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letter_project.settings')

application = get_wsgi_application()
