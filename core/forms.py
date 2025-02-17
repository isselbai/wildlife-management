from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import MediaFile, Camera, Tag

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class MediaFileUploadForm(forms.Form):
    files = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Select Files',
        required=True,
        help_text='You can select multiple files by holding Ctrl (Windows) or Cmd (Mac) while selecting'
    )
    camera = forms.ModelChoiceField(
        queryset=Camera.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a camera",
        required=True
    )
    manual_capture_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text='Optional: Set this only if the image lacks EXIF data or you want to override it'
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags (comma-separated)',
            'data-role': 'tagsinput'
        }),
        required=False,
        help_text='Enter tags separated by commas (e.g., deer, bear, morning)'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter a description'
        }),
        required=False
    )

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Split tags and remove whitespace
            tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
            # Remove duplicates while preserving order
            return list(dict.fromkeys(tag_list))
        return []

class MediaSearchForm(forms.Form):
    camera = forms.ModelChoiceField(
        queryset=Camera.objects.all(),
        required=False,
        empty_label="All Cameras",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in descriptions...'
        })
    ) 