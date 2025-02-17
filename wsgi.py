"""
WSGI config for wildlife_management project.
"""

import os
import sys

# Add the project directory to the Python path
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildlife_management.settings')

application = get_wsgi_application() 