from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee list and dashboard
    path('', views.employee_list, name='list'),
    path('dashboard/', views.employee_dashboard, name='dashboard'),
    
    # Employee CRUD operations
    path('create/', views.employee_create, name='create'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
    path('<int:employee_id>/edit/', views.employee_edit, name='update'),
    path('<int:employee_id>/delete/', views.employee_delete, name='delete'),
    
    # ----  Additional URLs will be enabled once their views are implemented ----
    # Employee profile sections (pending implementation)
    # path('<int:employee_id>/personal/', views.employee_personal, name='personal'),
    # path('<int:employee_id>/employment/', views.employee_employment, name='employment'),
    # path('<int:employee_id>/financial/', views.employee_financial, name='financial'),

    # Document management (list / detail not yet implemented)
    # path('<int:employee_id>/documents/', views.document_list, name='documents'),
    path('<int:employee_id>/documents/upload/', views.upload_document, name='upload_document'),
    # path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    # path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:document_id>/verify/', views.verify_document, name='document_verify'),

    # Future endpoints (contacts, education, experience, transfers, promotions, reviews, APIs)
    # ... (commented out until corresponding views are available) ...
]
