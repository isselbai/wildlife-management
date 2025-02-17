from django.core.management.base import BaseCommand
from core.weather_utils import WeatherAPI
from django.conf import settings

class Command(BaseCommand):
    help = 'Test the OpenWeather API connection'

    def handle(self, *args, **options):
        self.stdout.write('Testing OpenWeather API connection...\n')
        
        # Check if API key is configured
        if not settings.OPENWEATHER_API_KEY:
            self.stderr.write(self.style.ERROR(
                'OpenWeather API key not found in settings!'
            ))
            return
        
        self.stdout.write(f'Using API key: {settings.OPENWEATHER_API_KEY[:6]}...\n')
        
        # Initialize API client
        api = WeatherAPI()
        
        # Test coordinates (San Francisco, CA)
        test_lat = 37.7749
        test_lon = -122.4194
        
        self.stdout.write(f'Testing with coordinates: {test_lat}, {test_lon}\n')
        
        # Attempt to fetch weather data
        try:
            weather_data = api.get_weather_data(test_lat, test_lon)
            
            if weather_data:
                self.stdout.write(self.style.SUCCESS(
                    'Successfully connected to OpenWeather API!\n'
                ))
                self.stdout.write('Test location weather data:')
                self.stdout.write(f"Temperature: {weather_data['temperature']}°C")
                self.stdout.write(f"Condition: {weather_data['weather_condition']}")
                self.stdout.write(f"Humidity: {weather_data['humidity']}%")
                self.stdout.write(f"Wind Speed: {weather_data['wind_speed']} m/s")
                self.stdout.write(f"Data Timestamp: {weather_data['data_timestamp']}")
            else:
                self.stderr.write(self.style.ERROR(
                    'Failed to fetch weather data. Check the logs for details.'
                ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Error testing API connection: {str(e)}'
            )) 