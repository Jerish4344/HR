from django.urls import path
from . import views

app_name = 'accommodation'

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # Accommodation management
    path('manage/', views.manage, name='manage'),
    
    # Accommodation listings
    path('list/', views.accommodation_list, name='list'),
    path('add/', views.add_accommodation, name='add'),
    path('<int:accommodation_id>/', views.accommodation_detail, name='detail'),
    path('<int:accommodation_id>/edit/', views.edit_accommodation, name='edit'),
    
    # Allocation management
    path('allocations/', views.allocations, name='allocations'),
    path('allocate/', views.allocate_accommodation, name='allocate'),
    path('allocations/<int:allocation_id>/', views.allocation_detail, name='allocation_detail'),
    
    # Requests
    path('requests/', views.accommodation_requests, name='requests'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]
