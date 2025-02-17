from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from PIL import Image
from PIL.ExifTags import TAGS
import os
import hashlib

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Camera(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90.0, message="Latitude must be between -90 and 90 degrees"),
            MaxValueValidator(90.0, message="Latitude must be between -90 and 90 degrees")
        ]
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180.0, message="Longitude must be between -180 and 180 degrees"),
            MaxValueValidator(180.0, message="Longitude must be between -180 and 180 degrees")
        ]
    )
    orientation = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0, message="Orientation must be between 0 and 360 degrees"),
            MaxValueValidator(360.0, message="Orientation must be between 0 and 360 degrees")
        ],
        help_text="Camera orientation in degrees (0-360°, where 0° is North)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class MediaFile(models.Model):
    file = models.ImageField(
        upload_to='media/%Y/%m/%d/',
        help_text="Supported formats: JPG, PNG, GIF"
    )
    upload_date = models.DateTimeField(default=timezone.now)
    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='media_files'
    )
    description = models.TextField(blank=True)
    
    # EXIF-related fields
    capture_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the photo was taken (from EXIF data)"
    )
    camera_make = models.CharField(max_length=100, blank=True)
    camera_model = models.CharField(max_length=100, blank=True)
    exposure_time = models.CharField(max_length=50, blank=True)
    f_number = models.CharField(max_length=50, blank=True)
    iso_speed = models.CharField(max_length=50, blank=True)
    focal_length = models.CharField(max_length=50, blank=True)
    has_exif = models.BooleanField(default=False)
    
    # Duplicate and burst detection fields
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of the image file"
    )
    is_duplicate = models.BooleanField(
        default=False,
        help_text="Whether this file is a duplicate of another"
    )
    duplicate_of = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='duplicates',
        help_text="Reference to the original file if this is a duplicate"
    )
    burst_group = models.CharField(
        max_length=50,
        blank=True,
        help_text="Identifier for grouping burst photos"
    )
    burst_sequence = models.IntegerField(
        null=True,
        blank=True,
        help_text="Sequence number within a burst group"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.camera.name} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"

    def extract_exif_data(self):
        """Extract EXIF data from the image file if available."""
        if not self.file:
            return

        try:
            with Image.open(self.file.path) as img:
                if not hasattr(img, '_getexif') or img._getexif() is None:
                    return

                exif = {
                    TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in TAGS
                }

                # Extract DateTime
                if 'DateTimeOriginal' in exif:
                    try:
                        # EXIF DateTime format: 'YYYY:MM:DD HH:MM:SS'
                        date_str = exif['DateTimeOriginal']
                        self.capture_date = timezone.datetime.strptime(
                            date_str,
                            '%Y:%m:%d %H:%M:%S'
                        )
                    except (ValueError, TypeError):
                        pass

                # Extract camera information
                self.camera_make = exif.get('Make', '')[:100]
                self.camera_model = exif.get('Model', '')[:100]
                
                # Extract exposure information
                if 'ExposureTime' in exif:
                    exposure = exif['ExposureTime']
                    if isinstance(exposure, tuple):
                        self.exposure_time = f"{exposure[0]}/{exposure[1]}"
                
                if 'FNumber' in exif:
                    f_number = exif['FNumber']
                    if isinstance(f_number, tuple):
                        self.f_number = f"f/{f_number[0]/f_number[1]:.1f}"
                
                self.iso_speed = str(exif.get('ISOSpeedRatings', ''))
                
                if 'FocalLength' in exif:
                    focal = exif['FocalLength']
                    if isinstance(focal, tuple):
                        self.focal_length = f"{focal[0]/focal[1]:.1f}mm"

                self.has_exif = True
                self.save()

        except (IOError, AttributeError, KeyError, IndexError) as e:
            print(f"Error extracting EXIF data: {e}")

    def compute_file_hash(self):
        """Compute SHA-256 hash of the image file."""
        if not self.file:
            return None
        
        try:
            sha256_hash = hashlib.sha256()
            with open(self.file.path, "rb") as f:
                # Read the file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error computing file hash: {e}")
            return None

    def save(self, *args, **kwargs):
        # Compute file hash if not set
        if not self.file_hash and self.file:
            self.file_hash = self.compute_file_hash()
        
        # Check for duplicates and bursts
        if not self.pk:  # Only on creation
            self.check_duplicates()
            self.check_burst()
        
        # Save the model
        super().save(*args, **kwargs)
        
        # Fetch weather data after saving (needs the ID)
        if not hasattr(self, 'weather_data'):
            from .weather_utils import fetch_weather_for_media
            fetch_weather_for_media(self)

    class Meta:
        ordering = ['-upload_date']

class WeatherData(models.Model):
    media_file = models.OneToOneField(
        'MediaFile',
        on_delete=models.CASCADE,
        related_name='weather_data'
    )
    temperature = models.FloatField(
        help_text='Temperature in Celsius',
        null=True,
        blank=True
    )
    feels_like = models.FloatField(
        help_text='Feels like temperature in Celsius',
        null=True,
        blank=True
    )
    humidity = models.IntegerField(
        help_text='Humidity percentage',
        null=True,
        blank=True
    )
    wind_speed = models.FloatField(
        help_text='Wind speed in meters/sec',
        null=True,
        blank=True
    )
    wind_direction = models.IntegerField(
        help_text='Wind direction in degrees',
        null=True,
        blank=True
    )
    weather_condition = models.CharField(
        max_length=100,
        help_text='Weather condition description',
        null=True,
        blank=True
    )
    weather_icon = models.CharField(
        max_length=10,
        help_text='Weather condition icon code',
        null=True,
        blank=True
    )
    fetch_date = models.DateTimeField(
        auto_now_add=True,
        help_text='When this weather data was fetched'
    )
    data_timestamp = models.DateTimeField(
        help_text='Timestamp of the weather data'
    )

    def __str__(self):
        return f'Weather data for {self.media_file} at {self.data_timestamp}'

    class Meta:
        verbose_name = 'Weather Data'
        verbose_name_plural = 'Weather Data'
        indexes = [
            models.Index(fields=['data_timestamp']),
        ]
