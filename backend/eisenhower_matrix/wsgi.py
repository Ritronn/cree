"""
WSGI config for eisenhower_matrix project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eisenhower_matrix.settings')

application = get_wsgi_application()
