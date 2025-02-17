from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from .models import MediaFile, Tag, WeatherData

def get_basic_stats():
    """Get basic statistics about media files."""
    total_files = MediaFile.objects.count()
    buck_count = MediaFile.objects.filter(tags__name='buck').count()
    doe_count = MediaFile.objects.filter(tags__name='doe').count()
    
    return {
        'total_files': total_files,
        'buck_count': buck_count,
        'doe_count': doe_count
    }

def get_upload_timeline(days=30):
    """Get daily upload counts for the specified number of days."""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    daily_uploads = (
        MediaFile.objects
        .filter(upload_date__gte=start_date)
        .extra({'date': "DATE(upload_date)"})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    # Create a complete date range with zeros for missing dates
    date_counts = defaultdict(int)
    current_date = start_date.date()
    while current_date <= end_date.date():
        date_counts[current_date.isoformat()] = 0
        current_date += timedelta(days=1)
    
    # Fill in actual counts
    for entry in daily_uploads:
        date_counts[entry['date'].isoformat()] = entry['count']
    
    return {
        'labels': list(date_counts.keys()),
        'counts': list(date_counts.values())
    }

def get_weather_impact():
    """Analyze correlation between weather conditions and sightings."""
    weather_stats = (
        WeatherData.objects
        .filter(media_file__tags__name__in=['buck', 'doe'])
        .values(
            'weather_condition',
            'media_file__tags__name'
        )
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Organize data by weather condition
    weather_impact = defaultdict(lambda: {'buck': 0, 'doe': 0, 'total': 0})
    for stat in weather_stats:
        condition = stat['weather_condition']
        animal = stat['media_file__tags__name']
        count = stat['count']
        
        weather_impact[condition][animal] = count
        weather_impact[condition]['total'] += count
    
    # Convert to list and sort by total sightings
    impact_data = [
        {
            'condition': condition,
            'buck_count': data['buck'],
            'doe_count': data['doe'],
            'total': data['total']
        }
        for condition, data in weather_impact.items()
    ]
    impact_data.sort(key=lambda x: x['total'], reverse=True)
    
    return impact_data

def get_temperature_ranges():
    """Analyze sightings across temperature ranges."""
    temp_ranges = [
        {'min': float('-inf'), 'max': 0, 'label': 'Below 0°C'},
        {'min': 0, 'max': 10, 'label': '0-10°C'},
        {'min': 10, 'max': 20, 'label': '10-20°C'},
        {'min': 20, 'max': 30, 'label': '20-30°C'},
        {'min': 30, 'max': float('inf'), 'label': 'Above 30°C'}
    ]
    
    temp_stats = []
    for temp_range in temp_ranges:
        query = Q(temperature__gt=temp_range['min'])
        if temp_range['max'] != float('inf'):
            query &= Q(temperature__lte=temp_range['max'])
        
        stats = (
            WeatherData.objects
            .filter(query)
            .aggregate(
                total=Count('id'),
                buck_count=Count('media_file__tags', filter=Q(media_file__tags__name='buck')),
                doe_count=Count('media_file__tags', filter=Q(media_file__tags__name='doe'))
            )
        )
        
        temp_stats.append({
            'range': temp_range['label'],
            'total': stats['total'],
            'buck_count': stats['buck_count'],
            'doe_count': stats['doe_count']
        })
    
    return temp_stats 