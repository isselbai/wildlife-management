# Wildlife Management System

A Django-based wildlife management system for tracking and analyzing wildlife camera data with weather correlation and AI-powered animal classification.

## Features

- 📸 Media file management with EXIF data extraction
- 🦌 AI-powered deer classification (buck/doe)
- 🗺️ Camera location mapping
- 📊 Weather data correlation
- 📈 Statistical dashboard
- 🔄 Duplicate detection
- 📱 Responsive design

## Tech Stack

- Python 3.8+
- Django 4.2+
- PostgreSQL (Production)
- AWS S3 (Media Storage)
- Chart.js (Visualizations)
- Bootstrap 5 (UI)
- OpenWeather API (Weather Data)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wildlife-management.git
cd wildlife-management
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in project root:
```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
OPENWEATHER_API_KEY=your-openweather-api-key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Production Deployment

This project is configured for deployment on Railway.app with AWS S3 for media storage.

### Prerequisites

- Railway.app account
- AWS account with S3 bucket
- OpenWeather API key

### Environment Variables

Required environment variables in production:
```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<secure-secret-key>
DJANGO_ALLOWED_HOSTS=.railway.app
DATABASE_URL=<provided-by-railway>
USE_S3=True
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_STORAGE_BUCKET_NAME=<your-bucket>
AWS_S3_REGION_NAME=<your-region>
OPENWEATHER_API_KEY=<your-key>
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 