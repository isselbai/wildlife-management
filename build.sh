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

# Ensure __init__.py files exist and are not empty
echo "# Wildlife Management WSGI module" > wildlife_management/__init__.py
echo "# Core application module" > core/__init__.py

echo "Verifying project structure..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Explicitly set the project root
export PROJECT_ROOT="/opt/render/project/src"
echo "Project root: $PROJECT_ROOT"

# Set up Python path
echo "Setting up Python path..."
export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/wildlife_management:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH"

echo "Verifying Python imports..."
python -c "import sys; print('Python path:', sys.path)"
python -c "import wildlife_management; print('wildlife_management path:', wildlife_management.__file__)"

echo "Verifying WSGI application..."
python -c "from wildlife_management.wsgi import application; print('WSGI application loaded successfully')"
python -c "import wildlife_management.wsgi; print('WSGI module location:', wildlife_management.wsgi.__file__)"

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate

echo "Verifying static files..."
echo "Staticfiles directory contents:"
ls -la staticfiles/

echo "Creating verification file..."
echo "WSGI_APP=wildlife_management.wsgi:application" > .env.render

echo "Build script completed." 