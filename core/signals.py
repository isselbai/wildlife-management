from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MediaFile, Tag
# Temporarily comment out AI classifier for weather testing
# from .ai_classifier import classifier

@receiver(post_save, sender=MediaFile)
def classify_media_file(sender, instance, created, **kwargs):
    """Classify the media file after it's saved."""
    # Temporarily disable AI classification for weather testing
    pass
    # Original code commented out:
    # # Only process image files
    # if not instance.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
    #     return
    # 
    # # Skip if already has buck/doe tag
    # existing_tags = set(instance.tags.values_list('name', flat=True))
    # if 'buck' in existing_tags or 'doe' in existing_tags:
    #     return
    # 
    # # Run classification
    # predictions = classifier.predict(instance.file.path)
    # if predictions:
    #     best_label, confidence = classifier.get_best_prediction(predictions)
    #     if best_label:
    #         # Create or get the tag
    #         tag, _ = Tag.objects.get_or_create(name=best_label)
    #         # Add the tag to the media file
    #         instance.tags.add(tag)
    #         print(f"Added {best_label} tag with confidence {confidence:.2f} to {instance.file.name}") 