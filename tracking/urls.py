from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # View tracking data
    path('view/', views.view, name='view'),
    
    # Employee tracking details
    path('employee/<int:employee_id>/', views.employee_tracking, name='employee_tracking'),
    
    # Geofence management
    path('geofences/', views.geofence_list, name='geofence_list'),
    path('geofences/add/', views.add_geofence, name='add_geofence'),
    path('geofences/<int:geofence_id>/', views.geofence_detail, name='geofence_detail'),
    path('geofences/<int:geofence_id>/edit/', views.edit_geofence, name='edit_geofence'),
    
    # Device management
    path('devices/', views.device_list, name='device_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/location-history/', views.location_history, name='location_history'),
    
    # API endpoints for mobile app
    path('api/update-location/', views.api_update_location, name='api_update_location'),
    path('api/geofences/', views.api_geofences, name='api_geofences'),
]