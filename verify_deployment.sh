#!/bin/bash

# Exit on error and enable debug output
set -e
set -x

echo "=== Verifying Deployment Configuration ==="

echo "1. Checking Python environment:"
python --version
which python
echo "PYTHONPATH: $PYTHONPATH"

echo "2. Verifying project structure:"
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found in current directory"
    exit 1
fi

if [ ! -d "wildlife_management" ]; then
    echo "ERROR: wildlife_management directory not found"
    exit 1
fi

echo "3. Checking WSGI configuration:"
if [ ! -f "wildlife_management/wsgi.py" ]; then
    echo "ERROR: wsgi.py not found"
    exit 1
fi

echo "4. Verifying .env.render:"
if [ -f ".env.render" ]; then
    echo "Contents of .env.render:"
    cat .env.render
    echo "Testing .env.render:"
    source .env.render
    echo "WSGI_APP: $WSGI_APP"
    echo "PROJECT_ROOT: $PROJECT_ROOT"
    echo "PYTHONPATH: $PYTHONPATH"
else
    echo "ERROR: .env.render not found"
    exit 1
fi

echo "5. Testing WSGI imports:"
python -c "
import sys
print('Python path:', sys.path)
import wildlife_management
print('wildlife_management location:', wildlife_management.__file__)
from wildlife_management.wsgi import application
print('WSGI application successfully imported')
"

echo "6. Testing Gunicorn configuration:"
if ! command -v gunicorn &> /dev/null; then
    echo "ERROR: gunicorn not found"
    exit 1
fi

echo "7. Checking for conflicting files:"
for file in Procfile railway.json nixpacks.toml; do
    if [ -f "$file" ]; then
        echo "WARNING: Found potentially conflicting file: $file"
        echo "Contents of $file:"
        cat "$file"
    fi
done

echo "8. Verifying render.yaml configuration:"
if [ -f "render.yaml" ]; then
    echo "Contents of render.yaml:"
    cat render.yaml
else
    echo "ERROR: render.yaml not found"
    exit 1
fi

echo "=== Verification completed successfully ===" 