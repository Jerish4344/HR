from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # Generate reports
    path('generate/', views.generate, name='generate'),
    
    # Specific report types
    path('employee/', views.employee_report, name='employee_report'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('payroll/', views.payroll_report, name='payroll_report'),
    path('department/', views.department_report, name='department_report'),
    
    # Custom reports
    path('custom/', views.custom_report, name='custom_report'),
    path('custom/save/', views.save_custom_report, name='save_custom_report'),
    path('custom/<int:report_id>/', views.view_custom_report, name='view_custom_report'),
    
    # Export options
    path('export/pdf/<int:report_id>/', views.export_pdf, name='export_pdf'),
    path('export/excel/<int:report_id>/', views.export_excel, name='export_excel'),
    path('export/csv/<int:report_id>/', views.export_csv, name='export_csv'),
]
