from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum, Avg
from django.core.paginator import Paginator

# Import models (these would be created in models.py)
# from .models import PayrollPeriod, Payslip, SalaryStructure, SalaryComponent
# from employees.models import Employee


@login_required
def dashboard(request):
    """
    Main payroll dashboard showing payroll statistics and recent activities.
    """
    context = {
        'title': 'Payroll Dashboard',
        'current_month': timezone.now().strftime('%B %Y'),
        # 'total_payroll': Payslip.objects.filter(period__month=timezone.now().month, period__year=timezone.now().year).aggregate(Sum('net_salary'))['net_salary__sum'] or 0,
        # 'employee_count': Employee.objects.filter(is_active=True).count(),
        # 'pending_payslips': Payslip.objects.filter(status='pending').count(),
        # 'recent_payslips': Payslip.objects.order_by('-created_at')[:10],
    }
    return render(request, 'payroll/dashboard.html', context)


@login_required
@staff_member_required
def process_payroll(request):
    """
    View for processing payroll for a specific period.
    """
    if request.method == 'POST':
        # Process the payroll form
        # month = request.POST.get('month')
        # year = request.POST.get('year')
        # department_id = request.POST.get('department')
        
        # Create or get payroll period
        # period, created = PayrollPeriod.objects.get_or_create(
        #     month=month,
        #     year=year,
        #     defaults={'status': 'draft', 'created_by': request.user}
        # )
        
        # Process payroll for selected employees
        # employee_ids = request.POST.getlist('employee_ids')
        # for employee_id in employee_ids:
        #     process_employee_payroll(employee_id, period)
        
        messages.success(request, "Payroll processed successfully.")
        return redirect('payroll:dashboard')
    
    context = {
        'title': 'Process Payroll',
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
        # 'departments': Department.objects.filter(is_active=True),
        # 'employees': Employee.objects.filter(is_active=True),
    }
    return render(request, 'payroll/process_payroll.html', context)


@login_required
@staff_member_required
def salary_structures(request):
    """
    View to display list of salary structures.
    """
    # structures = SalaryStructure.objects.all()
    
    # Pagination
    # paginator = Paginator(structures, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Salary Structures',
        # 'page_obj': page_obj,
    }
    return render(request, 'payroll/salary_structures.html', context)


@login_required
@staff_member_required
def add_salary_structure(request):
    """
    View to add a new salary structure.
    """
    if request.method == 'POST':
        # Process the salary structure form
        # name = request.POST.get('name')
        # description = request.POST.get('description')
        # is_active = request.POST.get('is_active') == 'on'
        
        # Create salary structure
        # structure = SalaryStructure.objects.create(
        #     name=name,
        #     description=description,
        #     is_active=is_active,
        #     created_by=request.user
        # )
        
        # Add components to the structure
        # component_ids = request.POST.getlist('component_ids')
        # for component_id in component_ids:
        #     structure.components.add(component_id)
        
        messages.success(request, "Salary structure created successfully.")
        return redirect('payroll:salary_structures')
    
    context = {
        'title': 'Add Salary Structure',
        # 'components': SalaryComponent.objects.filter(is_active=True),
    }
    return render(request, 'payroll/salary_structure_form.html', context)


@login_required
@staff_member_required
def edit_salary_structure(request, structure_id):
    """
    View to edit an existing salary structure.
    """
    # structure = get_object_or_404(SalaryStructure, pk=structure_id)
    
    if request.method == 'POST':
        # Process the salary structure form
        # structure.name = request.POST.get('name')
        # structure.description = request.POST.get('description')
        # structure.is_active = request.POST.get('is_active') == 'on'
        # structure.updated_by = request.user
        # structure.save()
        
        # Update components
        # structure.components.clear()
        # component_ids = request.POST.getlist('component_ids')
        # for component_id in component_ids:
        #     structure.components.add(component_id)
        
        messages.success(request, "Salary structure updated successfully.")
        return redirect('payroll:salary_structures')
    
    context = {
        'title': 'Edit Salary Structure',
        # 'structure': structure,
        # 'components': SalaryComponent.objects.filter(is_active=True),
        # 'selected_components': structure.components.all().values_list('id', flat=True),
    }
    return render(request, 'payroll/salary_structure_form.html', context)


@login_required
@staff_member_required
def payslips(request):
    """
    View to display list of payslips with filtering options.
    """
    # Get filter parameters
    # month = request.GET.get('month')
    # year = request.GET.get('year')
    # department_id = request.GET.get('department')
    # employee_id = request.GET.get('employee')
    # status = request.GET.get('status')
    
    # Base queryset
    # payslips = Payslip.objects.all()
    
    # Apply filters
    # if month:
    #     payslips = payslips.filter(period__month=month)
    # if year:
    #     payslips = payslips.filter(period__year=year)
    # if department_id:
    #     payslips = payslips.filter(employee__department_id=department_id)
    # if employee_id:
    #     payslips = payslips.filter(employee_id=employee_id)
    # if status:
    #     payslips = payslips.filter(status=status)
    
    # Check if user is staff
    if not request.user.is_staff:
        # Show only the user's payslips
        # payslips = payslips.filter(employee=request.user.employee_profile)
        pass
    
    # Pagination
    # paginator = Paginator(payslips, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Payslips',
        # 'page_obj': page_obj,
        # 'departments': Department.objects.filter(is_active=True),
        # 'employees': Employee.objects.filter(is_active=True),
        # 'status_choices': Payslip.STATUS_CHOICES,
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
    }
    return render(request, 'payroll/payslips.html', context)


@login_required
def payslip_detail(request, payslip_id):
    """
    View to see details of a specific payslip.
    """
    # payslip = get_object_or_404(Payslip, pk=payslip_id)
    
    # Check if user has permission to view this payslip
    # if not request.user.is_staff and request.user.employee_profile != payslip.employee:
    #     messages.error(request, "You don't have permission to view this payslip.")
    #     return redirect('payroll:payslips')
    
    context = {
        'title': 'Payslip Details',
        # 'payslip': payslip,
        # 'earnings': payslip.components.filter(type='earning'),
        # 'deductions': payslip.components.filter(type='deduction'),
    }
    return render(request, 'payroll/payslip_detail.html', context)


@login_required
def download_payslip(request, payslip_id):
    """
    View to download a payslip as PDF.
    """
    # payslip = get_object_or_404(Payslip, pk=payslip_id)
    
    # Check if user has permission to download this payslip
    # if not request.user.is_staff and request.user.employee_profile != payslip.employee:
    #     messages.error(request, "You don't have permission to download this payslip.")
    #     return redirect('payroll:payslips')
    
    # Generate PDF
    # pdf = generate_payslip_pdf(payslip)
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{timezone.now().strftime("%Y%m%d")}.pdf"'
    # response.write(pdf)
    
    return response


@login_required
@staff_member_required
def salary_components(request):
    """
    View to display list of salary components.
    """
    # components = SalaryComponent.objects.all()
    
    # Pagination
    # paginator = Paginator(components, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Salary Components',
        # 'page_obj': page_obj,
    }
    return render(request, 'payroll/salary_components.html', context)


@login_required
@staff_member_required
def add_component(request):
    """
    View to add a new salary component.
    """
    if request.method == 'POST':
        # Process the component form
        # name = request.POST.get('name')
        # description = request.POST.get('description')
        # type = request.POST.get('type')  # earning or deduction
        # calculation_type = request.POST.get('calculation_type')  # fixed, percentage, formula
        # value = request.POST.get('value')
        # formula = request.POST.get('formula')
        # is_taxable = request.POST.get('is_taxable') == 'on'
        # is_active = request.POST.get('is_active') == 'on'
        
        # Create component
        # component = SalaryComponent.objects.create(
        #     name=name,
        #     description=description,
        #     type=type,
        #     calculation_type=calculation_type,
        #     value=value,
        #     formula=formula,
        #     is_taxable=is_taxable,
        #     is_active=is_active,
        #     created_by=request.user
        # )
        
        messages.success(request, "Salary component created successfully.")
        return redirect('payroll:components')
    
    context = {
        'title': 'Add Salary Component',
        # 'component_types': SalaryComponent.TYPE_CHOICES,
        # 'calculation_types': SalaryComponent.CALCULATION_TYPE_CHOICES,
    }
    return render(request, 'payroll/salary_component_form.html', context)


@login_required
@staff_member_required
def edit_component(request, component_id):
    """
    View to edit an existing salary component.
    """
    # component = get_object_or_404(SalaryComponent, pk=component_id)
    
    if request.method == 'POST':
        # Process the component form
        # component.name = request.POST.get('name')
        # component.description = request.POST.get('description')
        # component.type = request.POST.get('type')
        # component.calculation_type = request.POST.get('calculation_type')
        # component.value = request.POST.get('value')
        # component.formula = request.POST.get('formula')
        # component.is_taxable = request.POST.get('is_taxable') == 'on'
        # component.is_active = request.POST.get('is_active') == 'on'
        # component.updated_by = request.user
        # component.save()
        
        messages.success(request, "Salary component updated successfully.")
        return redirect('payroll:components')
    
    context = {
        'title': 'Edit Salary Component',
        # 'component': component,
        # 'component_types': SalaryComponent.TYPE_CHOICES,
        # 'calculation_types': SalaryComponent.CALCULATION_TYPE_CHOICES,
    }
    return render(request, 'payroll/salary_component_form.html', context)


@login_required
@staff_member_required
def payroll_reports(request):
    """
    View for payroll reports and analytics.
    """
    context = {
        'title': 'Payroll Reports',
        # 'departments': Department.objects.all(),
        # 'total_employees': Employee.objects.filter(is_active=True).count(),
        # 'payroll_summary': get_payroll_summary(),
    }
    return render(request, 'payroll/reports.html', context)


@login_required
@staff_member_required
def monthly_report(request):
    """
    View for monthly payroll report.
    """
    # Get filter parameters
    # month = request.GET.get('month', timezone.now().month)
    # year = request.GET.get('year', timezone.now().year)
    
    # Generate report data
    # report_data = generate_monthly_payroll_report(month, year)
    
    context = {
        'title': 'Monthly Payroll Report',
        # 'report_data': report_data,
        'month': timezone.now().month,
        'year': timezone.now().year,
    }
    return render(request, 'payroll/monthly_report.html', context)


@login_required
@staff_member_required
def department_report(request):
    """
    View for department-wise payroll report.
    """
    # Get filter parameters
    # month = request.GET.get('month', timezone.now().month)
    # year = request.GET.get('year', timezone.now().year)
    # department_id = request.GET.get('department')
    
    # Generate report data
    # report_data = generate_department_payroll_report(month, year, department_id)
    
    context = {
        'title': 'Department Payroll Report',
        # 'report_data': report_data,
        'month': timezone.now().month,
        'year': timezone.now().year,
        # 'departments': Department.objects.all(),
        # 'selected_department': department_id,
    }
    return render(request, 'payroll/department_report.html', context)


@login_required
def api_employee_salary(request, employee_id):
    """
    API endpoint to get salary details for a specific employee.
    """
    # Check if user has permission
    # if not request.user.is_staff and request.user.employee_profile.id != employee_id:
    #     return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # employee = get_object_or_404(Employee, pk=employee_id)
    # salary_structure = employee.salary_structure
    
    # if not salary_structure:
    #     return JsonResponse({'error': 'No salary structure assigned'}, status=404)
    
    # components = []
    # for component in salary_structure.components.all():
    #     components.append({
    #         'id': component.id,
    #         'name': component.name,
    #         'type': component.type,
    #         'value': calculate_component_value(component, employee),
    #     })
    
    # Sample data for demonstration
    data = {
        'employee_id': employee_id,
        'basic_salary': 50000,
        'gross_salary': 65000,
        'net_salary': 58000,
        'components': [
            {'name': 'Basic Salary', 'type': 'earning', 'value': 50000},
            {'name': 'HRA', 'type': 'earning', 'value': 10000},
            {'name': 'Transport Allowance', 'type': 'earning', 'value': 5000},
            {'name': 'Income Tax', 'type': 'deduction', 'value': 5000},
            {'name': 'Provident Fund', 'type': 'deduction', 'value': 2000},
        ]
    }
    
    return JsonResponse(data)
