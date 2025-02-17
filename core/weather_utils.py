import os
import logging
from datetime import datetime
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        if not self.api_key:
            logger.warning("OpenWeather API key not found in settings")
        else:
            logger.info(f"Using API key: {self.api_key[:6]}...")
    
    def get_weather_data(self, lat, lon, timestamp=None):
        """
        Fetch weather data for a given location and time.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            timestamp (datetime, optional): Timestamp for historical data.
                        If None, current weather will be fetched.
        
        Returns:
            dict: Weather data or None if request fails
        """
        if not self.api_key:
            logger.error("Cannot fetch weather data: API key not configured")
            return None
            
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'  # Use Celsius for temperature
        }
        
        try:
            logger.info(f"Fetching weather data for coordinates: {lat}, {lon}")
            response = requests.get(self.BASE_URL, params=params)
            
            if response.status_code == 401:
                logger.error("API key unauthorized. Please check if the key is valid and activated.")
                return None
            elif response.status_code == 429:
                logger.error("API rate limit exceeded.")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            logger.info("Successfully fetched weather data")
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg'),
                'weather_condition': data['weather'][0]['description'],
                'weather_icon': data['weather'][0]['icon'],
                'data_timestamp': datetime.fromtimestamp(data['dt'])
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"API response: {e.response.text}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None

def fetch_weather_for_media(media_file):
    """
    Fetch and save weather data for a media file.
    
    Args:
        media_file (MediaFile): The media file to fetch weather data for
    
    Returns:
        WeatherData: The created/updated weather data object or None if failed
    """
    from .models import WeatherData  # Import here to avoid circular imports
    
    # Skip if no camera or location data
    if not media_file.camera or not media_file.camera.latitude or not media_file.camera.longitude:
        logger.warning(f"Cannot fetch weather: no location data for media file {media_file.id}")
        return None
    
    # Use capture date if available, otherwise upload date
    timestamp = media_file.capture_date or media_file.upload_date
    
    # Fetch weather data
    weather_api = WeatherAPI()
    weather_data = weather_api.get_weather_data(
        lat=media_file.camera.latitude,
        lon=media_file.camera.longitude,
        timestamp=timestamp
    )
    
    if not weather_data:
        return None
    
    # Create or update weather data
    weather_obj, created = WeatherData.objects.update_or_create(
        media_file=media_file,
        defaults={
            'temperature': weather_data['temperature'],
            'feels_like': weather_data['feels_like'],
            'humidity': weather_data['humidity'],
            'wind_speed': weather_data['wind_speed'],
            'wind_direction': weather_data['wind_direction'],
            'weather_condition': weather_data['weather_condition'],
            'weather_icon': weather_data['weather_icon'],
            'data_timestamp': weather_data['data_timestamp']
        }
    )
    
    return weather_obj 