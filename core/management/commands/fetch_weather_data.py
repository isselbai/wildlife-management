from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import MediaFile
from core.weather_utils import fetch_weather_for_media
from datetime import datetime
import time

class Command(BaseCommand):
    help = 'Fetch weather data for media files that do not have it'

    def add_arguments(self, parser):
        parser.add_argument(
            '--camera',
            type=int,
            help='Only process files from this camera ID'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Only process files uploaded after this date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='Only process files uploaded before this date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing weather data and fetch again'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of files to process in each batch'
        )

    def handle(self, *args, **options):
        # Build queryset based on filters
        queryset = MediaFile.objects.select_related('camera')
        
        if options['camera']:
            queryset = queryset.filter(camera_id=options['camera'])
        
        if options['start_date']:
            try:
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d')
                queryset = queryset.filter(upload_date__date__gte=start_date)
            except ValueError:
                self.stderr.write('Invalid start date format. Use YYYY-MM-DD')
                return
        
        if options['end_date']:
            try:
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d')
                queryset = queryset.filter(upload_date__date__lte=end_date)
            except ValueError:
                self.stderr.write('Invalid end date format. Use YYYY-MM-DD')
                return
        
        # If reset option is used, clear existing weather data
        if options['reset']:
            self.stdout.write('Clearing existing weather data...')
            queryset.filter(weather_data__isnull=False).delete()
        else:
            # Only process files without weather data
            queryset = queryset.filter(weather_data__isnull=True)
        
        total_count = queryset.count()
        if total_count == 0:
            self.stdout.write('No media files to process')
            return
        
        self.stdout.write(f'Processing {total_count} media files...')
        processed = 0
        success = 0
        batch_size = options['batch_size']
        
        # Process in batches
        for i in range(0, total_count, batch_size):
            batch = queryset[i:i + batch_size]
            with transaction.atomic():
                for media_file in batch:
                    processed += 1
                    if fetch_weather_for_media(media_file):
                        success += 1
                    
                    # Show progress
                    if processed % 10 == 0:
                        self.stdout.write(f'Processed {processed}/{total_count} files...')
                    
                    # Small delay to avoid API rate limits
                    time.sleep(0.1)
        
        self.stdout.write(self.style.SUCCESS(
            f'Finished processing {processed} files. '
            f'Successfully fetched weather data for {success} files.'
        )) 