from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta
from django.template.defaultfilters import filesizeformat
from .forms import CustomUserCreationForm, MediaFileUploadForm, MediaSearchForm
from .models import MediaFile, Tag, Camera
from .dashboard_utils import (
    get_basic_stats,
    get_upload_timeline,
    get_weather_impact,
    get_temperature_ranges
)

def home(request):
    return render(request, 'core/home.html')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

@login_required
def profile(request):
    return render(request, 'core/profile.html')

@login_required
def upload_media(request):
    if request.method == 'POST':
        form = MediaFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    camera = form.cleaned_data['camera']
                    description = form.cleaned_data['description']
                    tag_names = form.cleaned_data['tags']
                    manual_capture_date = form.cleaned_data.get('manual_capture_date')
                    
                    # Process tags
                    tags = []
                    for tag_name in tag_names:
                        tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                        tags.append(tag)
                    
                    # Process each uploaded file
                    files = request.FILES.getlist('files')
                    uploaded_count = 0
                    for file in files:
                        media = MediaFile.objects.create(
                            file=file,
                            camera=camera,
                            description=description
                        )
                        
                        # Set manual capture date if provided (this will override EXIF data)
                        if manual_capture_date:
                            media.capture_date = manual_capture_date
                            media.save()
                        
                        media.tags.set(tags)
                        uploaded_count += 1
                    
                    # Prepare success message with EXIF information
                    exif_count = MediaFile.objects.filter(
                        id__in=[m.id for m in MediaFile.objects.order_by('-id')[:uploaded_count]],
                        has_exif=True
                    ).count()
                    
                    message = f'Successfully uploaded {uploaded_count} files. '
                    if exif_count > 0:
                        message += f'EXIF data extracted from {exif_count} files.'
                    
                    messages.success(request, message)
                    return redirect('media_list')
            except Exception as e:
                messages.error(request, f'Error uploading files: {str(e)}')
    else:
        form = MediaFileUploadForm()
    
    return render(request, 'core/upload_media.html', {'form': form})

@login_required
def media_list(request):
    form = MediaSearchForm(request.GET)
    media_files = MediaFile.objects.select_related('camera').prefetch_related('tags').all()

    if form.is_valid():
        # Filter by camera
        if form.cleaned_data.get('camera'):
            media_files = media_files.filter(camera=form.cleaned_data['camera'])
        
        # Filter by tag
        if form.cleaned_data.get('tag'):
            media_files = media_files.filter(tags=form.cleaned_data['tag'])
        
        # Filter by date range
        if form.cleaned_data.get('start_date'):
            media_files = media_files.filter(
                upload_date__date__gte=form.cleaned_data['start_date']
            )
        if form.cleaned_data.get('end_date'):
            media_files = media_files.filter(
                upload_date__date__lte=form.cleaned_data['end_date']
            )
        
        # Search in descriptions
        if form.cleaned_data.get('search_query'):
            query = form.cleaned_data['search_query']
            media_files = media_files.filter(
                Q(description__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(camera__name__icontains=query)
            ).distinct()

    # Add file type information for template rendering
    for media_file in media_files:
        media_file.file_type = 'video' if media_file.file.name.lower().endswith(
            ('.mp4', '.avi', '.mov', '.wmv')
        ) else 'image'

    context = {
        'form': form,
        'media_files': media_files,
        'total_count': media_files.count(),
    }
    return render(request, 'core/media_list.html', context)

@login_required
def camera_map(request):
    # Get date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base query for cameras with media count
    cameras = Camera.objects.annotate(
        media_count=Count('media_files'),
        latest_media_date=models.Max('media_files__upload_date')
    )
    
    # Apply date filters if provided
    if start_date:
        cameras = cameras.filter(media_files__upload_date__date__gte=start_date)
    if end_date:
        cameras = cameras.filter(media_files__upload_date__date__lte=end_date)
    
    # Get recent media for each camera
    for camera in cameras:
        recent_media = MediaFile.objects.filter(camera=camera).order_by('-upload_date')[:5]
        camera.recent_media = []
        camera.recent_media_json = []
        
        for media in recent_media:
            if media.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                thumbnail_url = media.file.url
                camera.recent_media.append({
                    'id': media.id,
                    'thumbnail_url': thumbnail_url
                })
                camera.recent_media_json.append({
                    'id': media.id,
                    'thumbnail_url': thumbnail_url
                })
    
    # Calculate map center
    if cameras:
        avg_lat = sum(c.latitude for c in cameras) / len(cameras)
        avg_lon = sum(c.longitude for c in cameras) / len(cameras)
    else:
        # Default to a central US location if no cameras
        avg_lat = 39.8283
        avg_lon = -98.5795
    
    context = {
        'cameras': cameras,
        'map_center': {
            'lat': avg_lat,
            'lon': avg_lon
        },
        'map_zoom': 4,  # Adjust based on your needs
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'core/camera_map.html', context)

@login_required
def manage_duplicates(request):
    # Get filter parameters
    camera_id = request.GET.get('camera')
    sort_by = request.GET.get('sort', 'date')
    
    # Base queryset for duplicates
    duplicates = MediaFile.objects.filter(
        is_duplicate=True,
        duplicate_of__isnull=False
    ).select_related('camera', 'duplicate_of')
    
    # Apply camera filter if specified
    if camera_id:
        duplicates = duplicates.filter(camera_id=camera_id)
    
    # Apply sorting
    if sort_by == 'date':
        duplicates = duplicates.order_by('-upload_date')
    elif sort_by == 'similarity':
        duplicates = duplicates.order_by('camera', 'duplicate_of', '-upload_date')
    elif sort_by == 'size':
        duplicates = duplicates.order_by('-file')  # This will sort by file size
    
    # Get statistics
    total_duplicates = duplicates.count()
    duplicate_storage = duplicates.aggregate(
        total_size=Sum('file')
    )['total_size'] or 0
    affected_cameras = duplicates.values('camera').distinct().count()
    
    # Create pairs of original and duplicate files
    duplicate_pairs = []
    for duplicate in duplicates:
        duplicate_pairs.append((duplicate.duplicate_of, duplicate))
    
    context = {
        'duplicate_pairs': duplicate_pairs,
        'total_duplicates': total_duplicates,
        'duplicate_storage': duplicate_storage,
        'affected_cameras': affected_cameras,
        'cameras': Camera.objects.all(),
        'selected_camera': int(camera_id) if camera_id else None,
        'sort_by': sort_by
    }
    
    return render(request, 'core/manage_duplicates.html', context)

@login_required
def delete_duplicate(request, media_id):
    if request.method == 'POST':
        media_file = get_object_or_404(MediaFile, id=media_id, is_duplicate=True)
        try:
            # Store info for success message
            camera_name = media_file.camera.name
            file_name = media_file.file.name
            
            # Delete the file and database record
            media_file.file.delete(save=False)  # Delete actual file
            media_file.delete()  # Delete database record
            
            messages.success(
                request,
                f'Successfully deleted duplicate file {file_name} from camera {camera_name}'
            )
        except Exception as e:
            messages.error(request, f'Error deleting duplicate: {str(e)}')
    
    # Redirect back to the manage duplicates page with the same filters
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('manage_duplicates')))

@login_required
def mark_not_duplicate(request, media_id):
    if request.method == 'POST':
        media_file = get_object_or_404(MediaFile, id=media_id, is_duplicate=True)
        try:
            # Remove duplicate marking
            media_file.is_duplicate = False
            media_file.duplicate_of = None
            media_file.save()
            
            messages.success(
                request,
                f'Marked file as not a duplicate: {media_file.file.name}'
            )
        except Exception as e:
            messages.error(request, f'Error updating duplicate status: {str(e)}')
    
    # Redirect back to the manage duplicates page with the same filters
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('manage_duplicates')))

@login_required
def batch_delete_duplicates(request):
    if request.method == 'POST':
        duplicate_ids = request.POST.getlist('selected_duplicates')
        if not duplicate_ids:
            messages.warning(request, 'No duplicates selected for deletion.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('manage_duplicates')))
        
        try:
            with transaction.atomic():
                # Get all selected duplicates
                duplicates = MediaFile.objects.filter(
                    id__in=duplicate_ids,
                    is_duplicate=True
                ).select_related('camera')
                
                # Store counts for success message
                total_count = duplicates.count()
                total_size = sum(d.file.size for d in duplicates)
                
                # Delete files and records
                for duplicate in duplicates:
                    duplicate.file.delete(save=False)  # Delete actual file
                    duplicate.delete()  # Delete database record
                
                messages.success(
                    request,
                    f'Successfully deleted {total_count} duplicate files, freeing up {filesizeformat(total_size)}'
                )
        except Exception as e:
            messages.error(request, f'Error deleting duplicates: {str(e)}')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('manage_duplicates')))

@login_required
def dashboard(request):
    """Display dashboard with various statistics and charts."""
    # Get basic statistics
    basic_stats = get_basic_stats()
    
    # Get upload timeline data
    timeline_data = get_upload_timeline()
    
    # Get weather impact data
    weather_impact = get_weather_impact()
    
    # Get temperature range statistics
    temp_stats = get_temperature_ranges()
    
    context = {
        'basic_stats': basic_stats,
        'timeline_data': timeline_data,
        'weather_impact': weather_impact,
        'temp_stats': temp_stats
    }
    
    return render(request, 'core/dashboard.html', context)
