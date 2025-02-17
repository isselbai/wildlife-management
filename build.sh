#!/bin/bash

# Exit on error
set -e

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

# Upgrade pip and install dependencies
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create static directory if it doesn't exist
mkdir -p static 