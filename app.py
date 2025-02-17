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

from wildlife_management.wsgi import application 