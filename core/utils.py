from datetime import timedelta
from django.utils import timezone
from django.db.models import Max
import imagehash
from PIL import Image

def compute_image_hash(image_path):
    """Compute perceptual hash of an image using ImageHash."""
    try:
        with Image.open(image_path) as img:
            # Convert to grayscale to focus on structure
            if img.mode != 'L':
                img = img.convert('L')
            # Compute average hash (can also use other algorithms like phash or dhash)
            return str(imagehash.average_hash(img))
    except Exception as e:
        print(f"Error computing image hash: {e}")
        return None

def check_duplicates(media_file):
    """Check if the media file is a duplicate of existing files."""
    from .models import MediaFile  # Import here to avoid circular import
    
    # Skip if no file hash
    if not media_file.file_hash:
        return
    
    # Look for exact duplicates first (same file hash)
    duplicates = MediaFile.objects.filter(
        file_hash=media_file.file_hash,
        camera=media_file.camera
    ).exclude(id=media_file.id)
    
    if duplicates.exists():
        # Mark as duplicate of the oldest file
        original = duplicates.order_by('upload_date').first()
        media_file.is_duplicate = True
        media_file.duplicate_of = original
        return
    
    # If no exact duplicates, check for near-duplicates using perceptual hash
    perceptual_hash = compute_image_hash(media_file.file.path)
    if not perceptual_hash:
        return
    
    # Get all media files from the same camera within a reasonable time window
    time_window = timedelta(minutes=5)
    potential_matches = MediaFile.objects.filter(
        camera=media_file.camera,
        upload_date__range=(
            media_file.upload_date - time_window,
            media_file.upload_date + time_window
        )
    ).exclude(id=media_file.id)
    
    for potential_match in potential_matches:
        match_hash = compute_image_hash(potential_match.file.path)
        if match_hash and hamming_distance(perceptual_hash, match_hash) < 5:  # Adjust threshold as needed
            media_file.is_duplicate = True
            media_file.duplicate_of = potential_match
            return

def check_burst(media_file):
    """Check if the media file is part of a burst sequence."""
    from .models import MediaFile  # Import here to avoid circular import
    
    # Only process files with capture_date
    if not media_file.capture_date:
        return
    
    # Define burst parameters
    burst_window = timedelta(seconds=2)  # Photos taken within 2 seconds
    
    # Look for nearby photos from the same camera
    nearby_photos = MediaFile.objects.filter(
        camera=media_file.camera,
        capture_date__range=(
            media_file.capture_date - burst_window,
            media_file.capture_date + burst_window
        )
    ).exclude(id=media_file.id)
    
    if nearby_photos.exists():
        # Check if there's an existing burst group to join
        existing_group = nearby_photos.filter(burst_group__isnull=False).first()
        
        if existing_group:
            # Join existing burst group
            media_file.burst_group = existing_group.burst_group
            # Get next sequence number
            max_sequence = MediaFile.objects.filter(
                burst_group=existing_group.burst_group
            ).aggregate(Max('burst_sequence'))['burst_sequence__max'] or 0
            media_file.burst_sequence = max_sequence + 1
        else:
            # Create new burst group
            from uuid import uuid4
            burst_group = f"burst_{uuid4().hex[:8]}"
            media_file.burst_group = burst_group
            media_file.burst_sequence = 1
            
            # Update nearby photos to be part of this burst
            for i, photo in enumerate(nearby_photos.order_by('capture_date')):
                photo.burst_group = burst_group
                photo.burst_sequence = i + 2  # Start from 2 since current photo is 1
                photo.save()

def hamming_distance(hash1, hash2):
    """Calculate the Hamming distance between two hash strings."""
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) 