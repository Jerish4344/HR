from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    # Main dashboard view
    path('', views.dashboard, name='dashboard'),
    
    # Payroll processing
    path('process/', views.process_payroll, name='process'),
    
    # Salary structures
    path('salary-structures/', views.salary_structures, name='salary_structures'),
    path('salary-structures/add/', views.add_salary_structure, name='add_salary_structure'),
    path('salary-structures/<int:structure_id>/', views.edit_salary_structure, name='edit_salary_structure'),
    
    # Payslips
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/<int:payslip_id>/', views.payslip_detail, name='payslip_detail'),
    path('payslips/<int:payslip_id>/download/', views.download_payslip, name='download_payslip'),
    
    # Salary components
    path('components/', views.salary_components, name='components'),
    path('components/add/', views.add_component, name='add_component'),
    path('components/<int:component_id>/', views.edit_component, name='edit_component'),
    
    # Reports
    path('reports/', views.payroll_reports, name='reports'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('reports/department/', views.department_report, name='department_report'),
    
    # API endpoints
    path('api/employee-salary/<int:employee_id>/', views.api_employee_salary, name='api_employee_salary'),
]
