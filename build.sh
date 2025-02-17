#!/bin/bash

# Exit on error
set -e

echo "Installing system dependencies..."
# Install system dependencies
apt-get update
apt-get install -y \
    python3-dev \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libmagic-dev

echo "Installing Python dependencies..."
# Upgrade pip and install dependencies
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Setting up project structure..."
# Ensure project structure is correct
mkdir -p static media staticfiles
touch wildlife_management/__init__.py
touch core/__init__.py

# Create symbolic link for root-level access
ln -sf wildlife_management/wsgi.py wsgi.py

echo "Verifying Python path..."
# Print Python path for debugging
python -c "import sys; print('Python path:', sys.path)"
python -c "import os; print('Current directory:', os.getcwd())"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate

echo "Final project structure:"
ls -R

echo "Build script completed." 