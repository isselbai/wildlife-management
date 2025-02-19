"""
WSGI config for wildlife_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Add the project root and the wildlife_management directory to Python path
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'wildlife_management'))

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildlife_management.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log any initialization errors
    import logging
    logging.error(f"Error loading WSGI application: {e}")
    raise
