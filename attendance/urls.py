from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # Mark attendance views
    path('mark/', views.mark_attendance, name='mark'),
    path('mark/bulk/', views.mark_attendance_bulk, name='mark_bulk'),
    
    # Leave management
    path('leaves/', views.leave_list, name='leaves'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:leave_id>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:leave_id>/approve/', views.leave_approve, name='leave_approve'),
    path('leaves/<int:leave_id>/reject/', views.leave_reject, name='leave_reject'),
    
    # Reports and analytics
    path('reports/', views.attendance_reports, name='reports'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('reports/employee/<int:employee_id>/', views.employee_report, name='employee_report'),
    
    # API endpoints
    path('api/status/', views.api_attendance_status, name='api_status'),
]
