from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # Dashboard - main interface after login
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Help and documentation
    path('help/', views.help_page, name='help'),
    
    # System settings (for admin users)
    path('settings/', views.system_settings, name='settings'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    
    # API endpoints for dashboard widgets
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
]
