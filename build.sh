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
# Create necessary directories with proper permissions
mkdir -p static media
mkdir -p staticfiles && chmod 755 staticfiles

# Ensure __init__.py files exist
touch wildlife_management/__init__.py
touch core/__init__.py

echo "Verifying project structure..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo "Verifying Python path..."
python -c "import sys; print('Python path:', sys.path)"

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate

echo "Verifying static files..."
echo "Staticfiles directory contents:"
ls -la staticfiles/

echo "Build script completed." 