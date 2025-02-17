# Wildlife Management System

A Django-based system for managing wildlife camera data and analysis.

## Requirements

- Python 3.11.7
- PostgreSQL (in production)
- Other dependencies listed in `requirements.txt`

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/isselbai/wildlife-management.git
   cd wildlife-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from example:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment on Railway

1. Fork this repository
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add required environment variables:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=.railway.app`
5. Deploy!

## Project Structure

```
wildlife_management/
├── core/                   # Main application
├── wildlife_management/    # Project settings
├── static/                # Static files
├── templates/             # HTML templates
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── railway.json         # Railway deployment config
```

## Features

- Image/Video Upload and Management
- Weather Data Integration
- Duplicate Detection
- Camera Location Mapping
- Analytics Dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 