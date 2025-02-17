from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(
        authentication_form=CustomAuthenticationForm,
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('media/upload/', views.upload_media, name='upload_media'),
    path('media/', views.media_list, name='media_list'),
    path('cameras/map/', views.camera_map, name='camera_map'),
    path('media/duplicates/', views.manage_duplicates, name='manage_duplicates'),
    path('media/duplicates/<int:media_id>/delete/', views.delete_duplicate, name='delete_duplicate'),
    path('media/duplicates/<int:media_id>/mark-not-duplicate/', views.mark_not_duplicate, name='mark_not_duplicate'),
    path('media/duplicates/batch-delete/', views.batch_delete_duplicates, name='batch_delete_duplicates'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('health/', views.health_check, name='health_check'),
] 