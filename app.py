"""
Fallback application entry point for Render.com
"""
import os
import sys
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Add the project root to Python path
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildlife_management.settings')

# Import and create the WSGI application
from django.core.wsgi import get_wsgi_application
app = application = get_wsgi_application() 