from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

# Local models
from .models import (
    Employee, EmployeeStatus,  # added EmployeeStatus
    EmployeeDocument, EmergencyContact, Education,
    WorkExperience, Skill, Language, EmployeeLanguage,
    EmployeeTransfer, EmployeePromotion, PerformanceReview
)
from core.models import Department, Store, Role, Document
from .forms import (
    EmployeeBasicForm, EmployeeContactForm, EmployeeEmploymentForm,
    EmployeeFinancialForm, EmployeeDocumentForm, EmergencyContactForm,
    EducationForm, WorkExperienceForm, LanguageProficiencyForm
)

import json
import csv
import io
import datetime


@login_required
def employee_list(request):
    """
    View to display list of employees with filtering options
    """
    # Get filter parameters from request
    department_id = request.GET.get('department')
    store_id = request.GET.get('store')
    status = request.GET.get('status')
    employment_type = request.GET.get('employment_type')
    
    # Base queryset
    employees = Employee.objects.filter(is_deleted=False)
    
    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if store_id:
        employees = employees.filter(store_id=store_id)
    
    if status:
        employees = employees.filter(status=status)
    
    if employment_type:
        employees = employees.filter(employment_type=employment_type)
    
    # Check if user is a manager and not staff
    if not request.user.is_staff:
        try:
            manager = request.user.employee_profile
            # Only show employees reporting to this manager
            employees = employees.filter(reporting_manager=manager)
        except:
            # If user doesn't have an employee profile, show nothing
            employees = Employee.objects.none()
    
    # Order by name
    employees = employees.order_by('first_name', 'last_name')
    
    # Pagination
    paginator = Paginator(employees, 20)  # Show 20 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get departments and stores for filters
    departments = Department.objects.filter(is_active=True)
    stores = Store.objects.filter(is_active=True)
    
    context = {
        'title': 'Employees',
        'page_obj': page_obj,
        'departments': departments,
        'stores': stores,
        'status_choices': EmployeeStatus.choices,
        'employment_type_choices': [
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('intern', 'Intern'),
            ('probation', 'Probation'),
            ('consultant', 'Consultant')
        ],
        'selected_filters': {
            'department': department_id,
            'store': store_id,
            'status': status,
            'employment_type': employment_type
        }
    }
    
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_dashboard(request):
    """
    High-level dashboard providing quick employee-related metrics.

    Shown mostly to HR/staff users.  For non-staff managers we scope
    the data to employees that report to them.
    """
    # Base queryset for employees (exclude deleted records)
    employees_qs = Employee.objects.filter(is_deleted=False)

    # If the requester is *not* staff, restrict to their subordinates
    if not request.user.is_staff:
        try:
            manager = request.user.employee_profile
            employees_qs = employees_qs.filter(reporting_manager=manager)
        except AttributeError:
            # User doesn’t have an employee profile; show empty set
            employees_qs = Employee.objects.none()

    # Compute metrics
    active_qs = employees_qs.filter(status='active')
    inactive_qs = employees_qs.exclude(status='active')

    recent_employees = employees_qs.order_by('-date_joined')[:10]

    # Pending performance reviews (last 10)
    pending_reviews = PerformanceReview.objects.filter(
        is_deleted=False,
        is_completed=False,
        employee__in=employees_qs,
    ).order_by('-created_at')[:10]

    context = {
        'title': 'Employee Dashboard',
        'active_employee_count': active_qs.count(),
        'inactive_employee_count': inactive_qs.count(),
        'recent_employees': recent_employees,
        'pending_reviews': pending_reviews,
    }

    return render(request, 'employees/dashboard.html', context)


@login_required
def employee_detail(request, employee_id):
    """
    View to display detailed information about an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    # Check if user has permission to view this employee
    if not request.user.is_staff and request.user.employee_profile != employee:
        if not hasattr(request.user, 'employee_profile') or employee.reporting_manager != request.user.employee_profile:
            raise PermissionDenied("You don't have permission to view this employee's details.")
    
    # Get related data
    documents = EmployeeDocument.objects.filter(employee=employee, is_deleted=False)
    emergency_contacts = EmergencyContact.objects.filter(employee=employee)
    education = Education.objects.filter(employee=employee, is_deleted=False)
    work_experience = WorkExperience.objects.filter(employee=employee, is_deleted=False)
    languages = EmployeeLanguage.objects.filter(employee=employee)
    skills = employee.skills.all()
    transfers = EmployeeTransfer.objects.filter(employee=employee).order_by('-effective_date')
    promotions = EmployeePromotion.objects.filter(employee=employee).order_by('-effective_date')
    performance_reviews = PerformanceReview.objects.filter(employee=employee, is_deleted=False).order_by('-review_period_end')
    
    # Get reporting employees (subordinates)
    subordinates = Employee.objects.filter(reporting_manager=employee, is_deleted=False)
    
    # Get active tab from request or default to 'personal'
    active_tab = request.GET.get('tab', 'personal')
    
    context = {
        'title': f'Employee: {employee.full_name}',
        'employee': employee,
        'documents': documents,
        'emergency_contacts': emergency_contacts,
        'education': education,
        'work_experience': work_experience,
        'languages': languages,
        'skills': skills,
        'transfers': transfers,
        'promotions': promotions,
        'performance_reviews': performance_reviews,
        'subordinates': subordinates,
        'active_tab': active_tab
    }
    
    return render(request, 'employees/employee_detail.html', context)


@login_required
@staff_member_required
def employee_create(request):
    """
    View to create a new employee
    """
    if request.method == 'POST':
        # Process the multi-step form submission
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Basic information form
            form = EmployeeBasicForm(request.POST, request.FILES)
            if form.is_valid():
                # Save form data to session
                request.session['employee_basic_data'] = form.cleaned_data
                if 'profile_picture' in request.FILES:
                    # Handle file upload separately
                    request.session['has_profile_picture'] = True
                
                return redirect('employees:create_step2')
        elif step == '2':
            # Contact information form
            form = EmployeeContactForm(request.POST)
            if form.is_valid():
                # Save form data to session
                request.session['employee_contact_data'] = form.cleaned_data
                return redirect('employees:create_step3')
        elif step == '3':
            # Employment information form
            form = EmployeeEmploymentForm(request.POST)
            if form.is_valid():
                # Save form data to session
                request.session['employee_employment_data'] = form.cleaned_data
                return redirect('employees:create_step4')
        elif step == '4':
            # Financial information form
            form = EmployeeFinancialForm(request.POST)
            if form.is_valid():
                # Create the employee from all the collected data
                try:
                    # Get data from session
                    basic_data = request.session.get('employee_basic_data', {})
                    contact_data = request.session.get('employee_contact_data', {})
                    employment_data = request.session.get('employee_employment_data', {})
                    financial_data = form.cleaned_data
                    
                    # Create user account
                    username = basic_data.get('employee_id').lower()
                    email = contact_data.get('official_email')
                    
                    # Check if username exists
                    if User.objects.filter(username=username).exists():
                        username = f"{username}_{basic_data.get('first_name').lower()[0]}"
                    
                    # Generate a random password
                    import random
                    import string
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=basic_data.get('first_name', ''),
                        last_name=basic_data.get('last_name', '')
                    )
                    
                    # Create employee
                    employee = Employee(
                        user=user,
                        employee_id=basic_data.get('employee_id'),
                        first_name=basic_data.get('first_name'),
                        middle_name=basic_data.get('middle_name'),
                        last_name=basic_data.get('last_name'),
                        date_of_birth=basic_data.get('date_of_birth'),
                        gender=basic_data.get('gender'),
                        marital_status=basic_data.get('marital_status'),
                        blood_group=basic_data.get('blood_group'),
                        nationality=basic_data.get('nationality'),
                        
                        # Contact information
                        primary_phone=contact_data.get('primary_phone'),
                        secondary_phone=contact_data.get('secondary_phone'),
                        personal_email=contact_data.get('personal_email'),
                        official_email=contact_data.get('official_email'),
                        
                        # Employment information
                        department_id=employment_data.get('department'),
                        store_id=employment_data.get('store'),
                        role_id=employment_data.get('role'),
                        reporting_manager_id=employment_data.get('reporting_manager'),
                        employment_type=employment_data.get('employment_type'),
                        date_joined=employment_data.get('date_joined'),
                        probation_end_date=employment_data.get('probation_end_date'),
                        notice_period_days=employment_data.get('notice_period_days'),
                        status=employment_data.get('status'),
                        
                        # Financial information
                        bank_name=financial_data.get('bank_name'),
                        bank_account_number=financial_data.get('bank_account_number'),
                        ifsc_code=financial_data.get('ifsc_code'),
                        pan_number=financial_data.get('pan_number'),
                        aadhar_number=financial_data.get('aadhar_number'),
                        uan_number=financial_data.get('uan_number'),
                        esic_number=financial_data.get('esic_number'),
                        
                        # System fields
                        created_by=request.user,
                        updated_by=request.user
                    )
                    
                    # Handle profile picture
                    if request.session.get('has_profile_picture'):
                        employee.profile_picture = request.FILES.get('profile_picture')
                    
                    employee.save()
                    
                    # Add skills if provided
                    if 'skills' in employment_data:
                        employee.skills.set(employment_data['skills'])
                    
                    # Clear session data
                    for key in ['employee_basic_data', 'employee_contact_data', 
                               'employee_employment_data', 'has_profile_picture']:
                        if key in request.session:
                            del request.session[key]
                    
                    messages.success(request, f"Employee {employee.full_name} created successfully. Username: {username}, Password: {password}")
                    return redirect('employees:detail', employee_id=employee.id)
                
                except Exception as e:
                    messages.error(request, f"Error creating employee: {str(e)}")
    else:
        # Initial form load
        form = EmployeeBasicForm()
    
    context = {
        'title': 'Create New Employee',
        'form': form,
        'step': 1
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
@staff_member_required
def employee_create_step2(request):
    """
    Step 2 of employee creation - Contact information
    """
    # Check if step 1 was completed
    if 'employee_basic_data' not in request.session:
        messages.error(request, "Please complete step 1 first.")
        return redirect('employees:create')
    
    if request.method == 'POST':
        form = EmployeeContactForm(request.POST)
    else:
        form = EmployeeContactForm()
    
    context = {
        'title': 'Create New Employee - Contact Information',
        'form': form,
        'step': 2
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
@staff_member_required
def employee_create_step3(request):
    """
    Step 3 of employee creation - Employment information
    """
    # Check if previous steps were completed
    if 'employee_basic_data' not in request.session or 'employee_contact_data' not in request.session:
        messages.error(request, "Please complete previous steps first.")
        return redirect('employees:create')
    
    if request.method == 'POST':
        form = EmployeeEmploymentForm(request.POST)
    else:
        form = EmployeeEmploymentForm()
    
    context = {
        'title': 'Create New Employee - Employment Information',
        'form': form,
        'step': 3
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
@staff_member_required
def employee_create_step4(request):
    """
    Step 4 of employee creation - Financial information
    """
    # Check if previous steps were completed
    if ('employee_basic_data' not in request.session or 
        'employee_contact_data' not in request.session or
        'employee_employment_data' not in request.session):
        messages.error(request, "Please complete previous steps first.")
        return redirect('employees:create')
    
    if request.method == 'POST':
        form = EmployeeFinancialForm(request.POST)
    else:
        form = EmployeeFinancialForm()
    
    context = {
        'title': 'Create New Employee - Financial Information',
        'form': form,
        'step': 4
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
@staff_member_required
def employee_edit(request, employee_id):
    """
    View to edit an existing employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    # Check if user has permission to edit this employee
    if not request.user.is_staff and request.user.employee_profile != employee:
        if not hasattr(request.user, 'employee_profile') or employee.reporting_manager != request.user.employee_profile:
            raise PermissionDenied("You don't have permission to edit this employee's details.")
    
    if request.method == 'POST':
        # Determine which form is being submitted
        form_type = request.POST.get('form_type')
        
        if form_type == 'basic':
            form = EmployeeBasicForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, "Basic information updated successfully.")
                return redirect('employees:detail', employee_id=employee.id)
        
        elif form_type == 'contact':
            form = EmployeeContactForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, "Contact information updated successfully.")
                return redirect('employees:detail', employee_id=employee.id)
        
        elif form_type == 'employment':
            form = EmployeeEmploymentForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, "Employment information updated successfully.")
                return redirect('employees:detail', employee_id=employee.id)
        
        elif form_type == 'financial':
            form = EmployeeFinancialForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, "Financial information updated successfully.")
                return redirect('employees:detail', employee_id=employee.id)
    
    # Get the form type from the request or default to 'basic'
    form_type = request.GET.get('form', 'basic')
    
    # Create the appropriate form
    if form_type == 'basic':
        form = EmployeeBasicForm(instance=employee)
        title = "Edit Basic Information"
    elif form_type == 'contact':
        form = EmployeeContactForm(instance=employee)
        title = "Edit Contact Information"
    elif form_type == 'employment':
        form = EmployeeEmploymentForm(instance=employee)
        title = "Edit Employment Information"
    elif form_type == 'financial':
        form = EmployeeFinancialForm(instance=employee)
        title = "Edit Financial Information"
    else:
        form = EmployeeBasicForm(instance=employee)
        title = "Edit Basic Information"
    
    context = {
        'title': title,
        'form': form,
        'employee': employee,
        'form_type': form_type
    }
    
    return render(request, 'employees/employee_edit.html', context)


@login_required
@staff_member_required
def employee_delete(request, employee_id):
    """
    View to soft delete an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    if request.method == 'POST':
        # Soft delete the employee
        employee.soft_delete(user=request.user)
        
        # Deactivate the associated user account
        if employee.user:
            employee.user.is_active = False
            employee.user.save()
        
        messages.success(request, f"Employee {employee.full_name} has been deleted.")
        return redirect('employees:list')
    
    context = {
        'title': 'Delete Employee',
        'employee': employee
    }
    
    return render(request, 'employees/employee_delete.html', context)


@login_required
def upload_document(request, employee_id):
    """
    View to upload documents for an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    # Check if user has permission to upload documents for this employee
    if not request.user.is_staff and request.user.employee_profile != employee:
        if not hasattr(request.user, 'employee_profile') or employee.reporting_manager != request.user.employee_profile:
            raise PermissionDenied("You don't have permission to upload documents for this employee.")
    
    if request.method == 'POST':
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the document first
            document = Document.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                file=form.cleaned_data['file'],
                document_type=form.cleaned_data['document_type'],
                expiry_date=form.cleaned_data['expiry_date'],
                created_by=request.user,
                updated_by=request.user
            )
            
            # Create the employee document
            employee_document = EmployeeDocument.objects.create(
                employee=employee,
                document=document,
                document_type=form.cleaned_data['document_type'],
                expiry_date=form.cleaned_data['expiry_date'],
                created_by=request.user,
                updated_by=request.user
            )
            
            messages.success(request, "Document uploaded successfully.")
            return redirect('employees:detail', employee_id=employee.id)
    else:
        form = EmployeeDocumentForm()
    
    context = {
        'title': f'Upload Document for {employee.full_name}',
        'form': form,
        'employee': employee
    }
    
    return render(request, 'employees/document_upload.html', context)


@login_required
@staff_member_required
def verify_document(request, document_id):
    """
    View to verify an employee document
    """
    document = get_object_or_404(EmployeeDocument, pk=document_id)
    
    if request.method == 'POST':
        document.verify(request.user.employee_profile)
        messages.success(request, "Document verified successfully.")
    
    return redirect('employees:detail', employee_id=document.employee.id)


@login_required
def employee_search(request):
    """
    View to search for employees
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search by name, employee ID, email, or phone
        employees = Employee.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(employee_id__icontains=query) | 
            Q(official_email__icontains=query) | 
            Q(personal_email__icontains=query) | 
            Q(primary_phone__icontains=query),
            is_deleted=False
        )
        
        # Check if user is a manager and not staff
        if not request.user.is_staff:
            try:
                manager = request.user.employee_profile
                # Only show employees reporting to this manager
                employees = employees.filter(reporting_manager=manager)
            except:
                # If user doesn't have an employee profile, show nothing
                employees = Employee.objects.none()
        
        # Pagination
        paginator = Paginator(employees, 20)  # Show 20 employees per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'title': 'Employee Search',
            'query': query,
            'page_obj': page_obj
        }
        
        return render(request, 'employees/employee_search.html', context)
    
    context = {
        'title': 'Employee Search'
    }
    
    return render(request, 'employees/employee_search.html', context)


@login_required
@staff_member_required
def add_emergency_contact(request, employee_id):
    """
    View to add an emergency contact for an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            emergency_contact = form.save(commit=False)
            emergency_contact.employee = employee
            emergency_contact.created_by = request.user
            emergency_contact.updated_by = request.user
            emergency_contact.save()
            
            messages.success(request, "Emergency contact added successfully.")
            return redirect('employees:detail', employee_id=employee.id)
    else:
        form = EmergencyContactForm()
    
    context = {
        'title': f'Add Emergency Contact for {employee.full_name}',
        'form': form,
        'employee': employee
    }
    
    return render(request, 'employees/emergency_contact_form.html', context)


@login_required
@staff_member_required
def add_education(request, employee_id):
    """
    View to add education details for an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.employee = employee
            education.created_by = request.user
            education.updated_by = request.user
            education.save()
            
            messages.success(request, "Education details added successfully.")
            return redirect('employees:detail', employee_id=employee.id)
    else:
        form = EducationForm()
    
    context = {
        'title': f'Add Education for {employee.full_name}',
        'form': form,
        'employee': employee
    }
    
    return render(request, 'employees/education_form.html', context)


@login_required
@staff_member_required
def add_work_experience(request, employee_id):
    """
    View to add work experience for an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.employee = employee
            experience.created_by = request.user
            experience.updated_by = request.user
            experience.save()
            
            messages.success(request, "Work experience added successfully.")
            return redirect('employees:detail', employee_id=employee.id)
    else:
        form = WorkExperienceForm()
    
    context = {
        'title': f'Add Work Experience for {employee.full_name}',
        'form': form,
        'employee': employee
    }
    
    return render(request, 'employees/work_experience_form.html', context)


@login_required
@staff_member_required
def add_language(request, employee_id):
    """
    View to add language proficiency for an employee
    """
    employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    if request.method == 'POST':
        form = LanguageProficiencyForm(request.POST)
        if form.is_valid():
            language_proficiency = form.save(commit=False)
            language_proficiency.employee = employee
            language_proficiency.save()
            
            messages.success(request, "Language proficiency added successfully.")
            return redirect('employees:detail', employee_id=employee.id)
    else:
        form = LanguageProficiencyForm()
    
    context = {
        'title': f'Add Language for {employee.full_name}',
        'form': form,
        'employee': employee
    }
    
    return render(request, 'employees/language_form.html', context)


@login_required
@staff_member_required
def export_employees(request):
    """
    View to export employees to CSV
    """
    # Get filter parameters from request
    department_id = request.GET.get('department')
    store_id = request.GET.get('store')
    status = request.GET.get('status')
    employment_type = request.GET.get('employment_type')
    
    # Base queryset
    employees = Employee.objects.filter(is_deleted=False)
    
    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if store_id:
        employees = employees.filter(store_id=store_id)
    
    if status:
        employees = employees.filter(status=status)
    
    if employment_type:
        employees = employees.filter(employment_type=employment_type)
    
    # Create the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'First Name', 'Middle Name', 'Last Name', 'Email',
        'Phone', 'Department', 'Store', 'Role', 'Status', 'Joined Date'
    ])
    
    for employee in employees:
        writer.writerow([
            employee.employee_id,
            employee.first_name,
            employee.middle_name or '',
            employee.last_name,
            employee.official_email,
            employee.primary_phone,
            employee.department.name if employee.department else '',
            employee.store.name if employee.store else '',
            employee.role.name if employee.role else '',
            employee.get_status_display(),
            employee.date_joined.strftime('%Y-%m-%d') if employee.date_joined else ''
        ])
    
    return response


@login_required
@require_POST
def employee_bulk_action(request):
    """
    View to perform bulk actions on selected employees
    """
    if not request.user.is_staff:
        raise PermissionDenied("You don't have permission to perform bulk actions.")
    
    selected_ids = request.POST.getlist('selected_employees')
    action = request.POST.get('bulk_action')
    
    if not selected_ids or not action:
        messages.error(request, "No employees selected or no action specified.")
        return redirect('employees:list')
    
    employees = Employee.objects.filter(id__in=selected_ids, is_deleted=False)
    
    if action == 'delete':
        # Soft delete the selected employees
        for employee in employees:
            employee.soft_delete(user=request.user)
            
            # Deactivate the associated user account
            if employee.user:
                employee.user.is_active = False
                employee.user.save()
        
        messages.success(request, f"{employees.count()} employees have been deleted.")
    
    elif action == 'change_status':
        new_status = request.POST.get('new_status')
        if new_status:
            # Update the status of selected employees
            employees.update(status=new_status, updated_by=request.user)
            messages.success(request, f"Status updated for {employees.count()} employees.")
    
    elif action == 'change_department':
        new_department_id = request.POST.get('new_department')
        if new_department_id:
            # Update the department of selected employees
            employees.update(department_id=new_department_id, updated_by=request.user)
            messages.success(request, f"Department updated for {employees.count()} employees.")
    
    return redirect('employees:list')


@login_required
def employee_profile(request):
    """
    View for an employee to view their own profile
    """
    try:
        employee = request.user.employee_profile
    except:
        messages.error(request, "Employee profile not found.")
        return redirect('core:dashboard')
    
    return redirect('employees:detail', employee_id=employee.id)
