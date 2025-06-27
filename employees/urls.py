from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee list and dashboard
    path('', views.employee_list, name='list'),
    path('dashboard/', views.employee_dashboard, name='dashboard'),
    
    # Employee CRUD operations
    path('create/', views.employee_create, name='create'),
    # Multi-step create wizard
    path('create/step2/', views.employee_create_step2, name='create_step2'),
    path('create/step3/', views.employee_create_step3, name='create_step3'),
    path('create/step4/', views.employee_create_step4, name='create_step4'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
    path('<int:employee_id>/edit/', views.employee_edit, name='update'),
    path('<int:employee_id>/delete/', views.employee_delete, name='delete'),

    # Export employees
    path('export/', views.export_employees, name='export'),
    # Bulk actions on employees
    path('bulk-action/', views.employee_bulk_action, name='bulk_action'),
    
    # ----  Additional URLs will be enabled once their views are implemented ----
    # Employee profile sections (pending implementation)
    # path('<int:employee_id>/personal/', views.employee_personal, name='personal'),
    # path('<int:employee_id>/employment/', views.employee_employment, name='employment'),
    # path('<int:employee_id>/financial/', views.employee_financial, name='financial'),

    # Document management
    path('<int:employee_id>/documents/', views.employee_documents, name='documents'),
    path('<int:employee_id>/documents/upload/', views.upload_document, name='upload_document'),
    # path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    # path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:document_id>/verify/', views.verify_document, name='document_verify'),

    # Employee additional information
    path('<int:employee_id>/contacts/', views.employee_contacts, name='contacts'),
    path('<int:employee_id>/education/', views.employee_education, name='education'),
    path('<int:employee_id>/experience/', views.employee_experience, name='experience'),

    # Create forms for additional information
    path('<int:employee_id>/contacts/add/', views.add_emergency_contact, name='add_contact'),
    path('<int:employee_id>/education/add/', views.add_education, name='add_education'),
    path('<int:employee_id>/experience/add/', views.add_work_experience, name='add_experience'),
    path('<int:employee_id>/language/add/', views.add_language, name='add_language'),

    # Future endpoints (contacts, education, experience, transfers, promotions, reviews, APIs)
    # ... (commented out until corresponding views are available) ...
]