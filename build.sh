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

echo "Creating necessary directories..."
# Create necessary directories
mkdir -p static media staticfiles

echo "Collecting static files..."
# Collect static files
python manage.py collectstatic --noinput

echo "Running database migrations..."
# Run migrations
python manage.py migrate

echo "Verifying project structure..."
# List project structure for debugging
ls -la
echo "Content of wildlife_management directory:"
ls -la wildlife_management/

echo "Checking for __init__.py..."
# Ensure __init__.py exists
touch wildlife_management/__init__.py
touch core/__init__.py

echo "Build script completed." 