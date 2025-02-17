"""
WSGI config for wildlife_management project.
"""

import os
import sys
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Add the project root and the wildlife_management directory to Python path
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'wildlife_management'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildlife_management.settings')

application = get_wsgi_application() 