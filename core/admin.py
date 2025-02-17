from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Camera, MediaFile, Tag

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'orientation', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('camera', 'upload_date', 'created_at')
    list_filter = ('camera', 'upload_date', 'tags')
    search_fields = ('camera__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
