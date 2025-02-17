from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import MediaFile
from core.utils import check_duplicates, check_burst
import time

class Command(BaseCommand):
    help = 'Process existing media files to detect duplicates and burst sequences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--camera',
            type=str,
            help='Process files only from a specific camera (by name)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing duplicate and burst information before processing'
        )

    def handle(self, *args, **options):
        # Get queryset based on options
        queryset = MediaFile.objects.all()
        if options['camera']:
            queryset = queryset.filter(camera__name=options['camera'])
        
        # Reset if requested
        if options['reset']:
            if options['dry_run']:
                self.stdout.write('Would reset duplicate and burst information')
            else:
                self.stdout.write('Resetting duplicate and burst information...')
                queryset.update(
                    is_duplicate=False,
                    duplicate_of=None,
                    burst_group='',
                    burst_sequence=None
                )
        
        total = queryset.count()
        self.stdout.write(f'Processing {total} files...')
        
        duplicates = 0
        bursts = 0
        start_time = time.time()
        
        # Process files
        for i, media_file in enumerate(queryset.iterator(), 1):
            if i % 100 == 0:
                self.stdout.write(f'Processed {i}/{total} files...')
            
            if not options['dry_run']:
                with transaction.atomic():
                    # Compute file hash if missing
                    if not media_file.file_hash:
                        media_file.file_hash = media_file.compute_file_hash() or ''
                        media_file.save()
                    
                    # Check for duplicates
                    was_duplicate = media_file.is_duplicate
                    check_duplicates(media_file)
                    if not was_duplicate and media_file.is_duplicate:
                        duplicates += 1
                    
                    # Check for bursts
                    had_burst = bool(media_file.burst_group)
                    check_burst(media_file)
                    if not had_burst and media_file.burst_group:
                        bursts += 1
            
            else:
                # In dry-run mode, just check what would be done
                if not media_file.file_hash:
                    self.stdout.write(f'Would compute hash for {media_file}')
                check_duplicates(media_file)
                if media_file.is_duplicate:
                    self.stdout.write(
                        f'Would mark {media_file} as duplicate of {media_file.duplicate_of}'
                    )
                check_burst(media_file)
                if media_file.burst_group:
                    self.stdout.write(
                        f'Would add {media_file} to burst group {media_file.burst_group}'
                    )
        
        elapsed = time.time() - start_time
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f'\nProcessed {total} files in {elapsed:.1f} seconds'
        ))
        if not options['dry_run']:
            self.stdout.write(f'Found {duplicates} new duplicates')
            self.stdout.write(f'Found {bursts} new burst sequences')
        else:
            self.stdout.write('Dry run completed - no changes made') 