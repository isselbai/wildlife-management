web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn wildlife_management.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 60 