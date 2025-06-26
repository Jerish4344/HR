from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

# Import models (these would be created in models.py)
# from .models import Accommodation, AccommodationType, Allocation, AccommodationRequest
# from employees.models import Employee


@login_required
def dashboard(request):
    """
    Main accommodation dashboard showing statistics and recent activities.
    """
    context = {
        'title': 'Accommodation Dashboard',
        # 'total_accommodations': Accommodation.objects.filter(is_active=True).count(),
        # 'occupied_count': Accommodation.objects.filter(is_active=True, status='occupied').count(),
        # 'available_count': Accommodation.objects.filter(is_active=True, status='available').count(),
        # 'pending_requests': AccommodationRequest.objects.filter(status='pending').count(),
        # 'recent_allocations': Allocation.objects.order_by('-created_at')[:10],
    }
    return render(request, 'accommodation/dashboard.html', context)


@login_required
@staff_member_required
def manage(request):
    """
    View for managing accommodation resources.
    """
    context = {
        'title': 'Manage Accommodation',
        # 'accommodation_types': AccommodationType.objects.all(),
        # 'total_accommodations': Accommodation.objects.filter(is_active=True).count(),
        # 'occupied_count': Accommodation.objects.filter(is_active=True, status='occupied').count(),
        # 'available_count': Accommodation.objects.filter(is_active=True, status='available').count(),
        # 'maintenance_count': Accommodation.objects.filter(is_active=True, status='maintenance').count(),
    }
    return render(request, 'accommodation/manage.html', context)


@login_required
def accommodation_list(request):
    """
    View to display list of accommodations with filtering options.
    """
    # Get filter parameters
    # accommodation_type = request.GET.get('type')
    # status = request.GET.get('status')
    # location = request.GET.get('location')
    
    # Base queryset
    # accommodations = Accommodation.objects.filter(is_active=True)
    
    # Apply filters
    # if accommodation_type:
    #     accommodations = accommodations.filter(type_id=accommodation_type)
    # if status:
    #     accommodations = accommodations.filter(status=status)
    # if location:
    #     accommodations = accommodations.filter(location__icontains=location)
    
    # Pagination
    # paginator = Paginator(accommodations, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Accommodation List',
        # 'page_obj': page_obj,
        # 'accommodation_types': AccommodationType.objects.all(),
        # 'status_choices': Accommodation.STATUS_CHOICES,
    }
    return render(request, 'accommodation/accommodation_list.html', context)


@login_required
@staff_member_required
def add_accommodation(request):
    """
    View to add a new accommodation.
    """
    if request.method == 'POST':
        # Process the accommodation form
        # name = request.POST.get('name')
        # type_id = request.POST.get('type')
        # location = request.POST.get('location')
        # address = request.POST.get('address')
        # capacity = request.POST.get('capacity')
        # rent = request.POST.get('rent')
        # status = request.POST.get('status')
        # description = request.POST.get('description')
        
        # Create accommodation
        # accommodation = Accommodation.objects.create(
        #     name=name,
        #     type_id=type_id,
        #     location=location,
        #     address=address,
        #     capacity=capacity,
        #     rent=rent,
        #     status=status,
        #     description=description,
        #     created_by=request.user,
        #     updated_by=request.user
        # )
        
        messages.success(request, "Accommodation added successfully.")
        return redirect('accommodation:list')
    
    context = {
        'title': 'Add Accommodation',
        # 'accommodation_types': AccommodationType.objects.all(),
        # 'status_choices': Accommodation.STATUS_CHOICES,
    }
    return render(request, 'accommodation/accommodation_form.html', context)


@login_required
def accommodation_detail(request, accommodation_id):
    """
    View to see details of a specific accommodation.
    """
    # accommodation = get_object_or_404(Accommodation, pk=accommodation_id, is_active=True)
    
    context = {
        'title': 'Accommodation Details',
        # 'accommodation': accommodation,
        # 'current_allocations': Allocation.objects.filter(accommodation=accommodation, is_active=True),
        # 'allocation_history': Allocation.objects.filter(accommodation=accommodation, is_active=False).order_by('-end_date'),
    }
    return render(request, 'accommodation/accommodation_detail.html', context)


@login_required
@staff_member_required
def edit_accommodation(request, accommodation_id):
    """
    View to edit an existing accommodation.
    """
    # accommodation = get_object_or_404(Accommodation, pk=accommodation_id, is_active=True)
    
    if request.method == 'POST':
        # Process the accommodation form
        # accommodation.name = request.POST.get('name')
        # accommodation.type_id = request.POST.get('type')
        # accommodation.location = request.POST.get('location')
        # accommodation.address = request.POST.get('address')
        # accommodation.capacity = request.POST.get('capacity')
        # accommodation.rent = request.POST.get('rent')
        # accommodation.status = request.POST.get('status')
        # accommodation.description = request.POST.get('description')
        # accommodation.updated_by = request.user
        # accommodation.save()
        
        messages.success(request, "Accommodation updated successfully.")
        return redirect('accommodation:detail', accommodation_id=accommodation_id)
    
    context = {
        'title': 'Edit Accommodation',
        # 'accommodation': accommodation,
        # 'accommodation_types': AccommodationType.objects.all(),
        # 'status_choices': Accommodation.STATUS_CHOICES,
    }
    return render(request, 'accommodation/accommodation_form.html', context)


@login_required
@staff_member_required
def allocations(request):
    """
    View to display list of accommodation allocations.
    """
    # Get filter parameters
    # accommodation_id = request.GET.get('accommodation')
    # employee_id = request.GET.get('employee')
    # status = request.GET.get('status')
    
    # Base queryset
    # allocations = Allocation.objects.all()
    
    # Apply filters
    # if accommodation_id:
    #     allocations = allocations.filter(accommodation_id=accommodation_id)
    # if employee_id:
    #     allocations = allocations.filter(employee_id=employee_id)
    # if status:
    #     if status == 'active':
    #         allocations = allocations.filter(is_active=True)
    #     elif status == 'inactive':
    #         allocations = allocations.filter(is_active=False)
    
    # Pagination
    # paginator = Paginator(allocations, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Accommodation Allocations',
        # 'page_obj': page_obj,
        # 'accommodations': Accommodation.objects.filter(is_active=True),
        # 'employees': Employee.objects.filter(is_active=True),
    }
    return render(request, 'accommodation/allocations.html', context)


@login_required
@staff_member_required
def allocate_accommodation(request):
    """
    View to allocate accommodation to an employee.
    """
    if request.method == 'POST':
        # Process the allocation form
        # accommodation_id = request.POST.get('accommodation')
        # employee_id = request.POST.get('employee')
        # start_date = request.POST.get('start_date')
        # end_date = request.POST.get('end_date')
        # rent = request.POST.get('rent')
        # notes = request.POST.get('notes')
        
        # Check if accommodation is available
        # accommodation = get_object_or_404(Accommodation, pk=accommodation_id, is_active=True)
        # if accommodation.status != 'available':
        #     messages.error(request, "This accommodation is not available for allocation.")
        #     return redirect('accommodation:allocate')
        
        # Create allocation
        # allocation = Allocation.objects.create(
        #     accommodation_id=accommodation_id,
        #     employee_id=employee_id,
        #     start_date=start_date,
        #     end_date=end_date,
        #     rent=rent,
        #     notes=notes,
        #     created_by=request.user,
        #     updated_by=request.user
        # )
        
        # Update accommodation status
        # accommodation.status = 'occupied'
        # accommodation.save()
        
        messages.success(request, "Accommodation allocated successfully.")
        return redirect('accommodation:allocations')
    
    context = {
        'title': 'Allocate Accommodation',
        # 'available_accommodations': Accommodation.objects.filter(is_active=True, status='available'),
        # 'employees': Employee.objects.filter(is_active=True),
    }
    return render(request, 'accommodation/allocate_form.html', context)


@login_required
def allocation_detail(request, allocation_id):
    """
    View to see details of a specific allocation.
    """
    # allocation = get_object_or_404(Allocation, pk=allocation_id)
    
    # Check if user has permission to view this allocation
    # if not request.user.is_staff and request.user.employee_profile != allocation.employee:
    #     messages.error(request, "You don't have permission to view this allocation.")
    #     return redirect('accommodation:allocations')
    
    context = {
        'title': 'Allocation Details',
        # 'allocation': allocation,
    }
    return render(request, 'accommodation/allocation_detail.html', context)


@login_required
def accommodation_requests(request):
    """
    View to display list of accommodation requests.
    """
    # Get filter parameters
    # status = request.GET.get('status')
    
    # Base queryset
    # requests = AccommodationRequest.objects.all()
    
    # Apply filters
    # if status:
    #     requests = requests.filter(status=status)
    
    # Check if user is staff
    if not request.user.is_staff:
        # Show only the user's requests
        # requests = requests.filter(employee=request.user.employee_profile)
        pass
    
    # Pagination
    # paginator = Paginator(requests, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Accommodation Requests',
        # 'page_obj': page_obj,
        # 'status_choices': AccommodationRequest.STATUS_CHOICES,
    }
    return render(request, 'accommodation/requests.html', context)


@login_required
def create_request(request):
    """
    View for an employee to request accommodation.
    """
    if request.method == 'POST':
        # Process the request form
        # accommodation_type_id = request.POST.get('accommodation_type')
        # preferred_location = request.POST.get('preferred_location')
        # reason = request.POST.get('reason')
        # required_from = request.POST.get('required_from')
        # family_size = request.POST.get('family_size')
        # additional_notes = request.POST.get('additional_notes')
        
        # Create request
        # accommodation_request = AccommodationRequest.objects.create(
        #     employee=request.user.employee_profile,
        #     accommodation_type_id=accommodation_type_id,
        #     preferred_location=preferred_location,
        #     reason=reason,
        #     required_from=required_from,
        #     family_size=family_size,
        #     additional_notes=additional_notes,
        #     status='pending'
        # )
        
        messages.success(request, "Accommodation request submitted successfully.")
        return redirect('accommodation:requests')
    
    context = {
        'title': 'Request Accommodation',
        # 'accommodation_types': AccommodationType.objects.all(),
    }
    return render(request, 'accommodation/request_form.html', context)


@login_required
def request_detail(request, request_id):
    """
    View to see details of a specific accommodation request.
    """
    # accommodation_request = get_object_or_404(AccommodationRequest, pk=request_id)
    
    # Check if user has permission to view this request
    # if not request.user.is_staff and request.user.employee_profile != accommodation_request.employee:
    #     messages.error(request, "You don't have permission to view this request.")
    #     return redirect('accommodation:requests')
    
    context = {
        'title': 'Request Details',
        # 'request': accommodation_request,
    }
    return render(request, 'accommodation/request_detail.html', context)


@login_required
@staff_member_required
def approve_request(request, request_id):
    """
    View to approve an accommodation request.
    """
    # accommodation_request = get_object_or_404(AccommodationRequest, pk=request_id)
    
    if request.method == 'POST':
        # accommodation_id = request.POST.get('accommodation')
        # notes = request.POST.get('notes')
        
        # Update request status
        # accommodation_request.status = 'approved'
        # accommodation_request.approved_by = request.user
        # accommodation_request.approved_date = timezone.now()
        # accommodation_request.notes = notes
        # accommodation_request.save()
        
        # Create allocation if accommodation is provided
        # if accommodation_id:
        #     allocation = Allocation.objects.create(
        #         accommodation_id=accommodation_id,
        #         employee=accommodation_request.employee,
        #         start_date=accommodation_request.required_from,
        #         notes=f"Allocated based on request #{accommodation_request.id}",
        #         created_by=request.user,
        #         updated_by=request.user
        #     )
            
        #     # Update accommodation status
        #     accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
        #     accommodation.status = 'occupied'
        #     accommodation.save()
        
        messages.success(request, "Accommodation request approved successfully.")
        return redirect('accommodation:request_detail', request_id=request_id)
    
    context = {
        'title': 'Approve Request',
        # 'request': accommodation_request,
        # 'available_accommodations': Accommodation.objects.filter(
        #     is_active=True, 
        #     status='available',
        #     type=accommodation_request.accommodation_type
        # ),
    }
    return render(request, 'accommodation/approve_request.html', context)


@login_required
@staff_member_required
def reject_request(request, request_id):
    """
    View to reject an accommodation request.
    """
    # accommodation_request = get_object_or_404(AccommodationRequest, pk=request_id)
    
    if request.method == 'POST':
        # rejection_reason = request.POST.get('rejection_reason')
        
        # Update request status
        # accommodation_request.status = 'rejected'
        # accommodation_request.rejected_by = request.user
        # accommodation_request.rejected_date = timezone.now()
        # accommodation_request.rejection_reason = rejection_reason
        # accommodation_request.save()
        
        messages.success(request, "Accommodation request rejected successfully.")
        return redirect('accommodation:request_detail', request_id=request_id)
    
    context = {
        'title': 'Reject Request',
        # 'request': accommodation_request,
    }
    return render(request, 'accommodation/reject_request.html', context)


@login_required
@staff_member_required
def reports(request):
    """
    View for accommodation reports and analytics.
    """
    # Get filter parameters
    # period = request.GET.get('period', 'monthly')
    # month = request.GET.get('month', timezone.now().month)
    # year = request.GET.get('year', timezone.now().year)
    
    context = {
        'title': 'Accommodation Reports',
        # 'occupancy_rate': calculate_occupancy_rate(),
        # 'allocation_by_department': get_allocation_by_department(),
        # 'accommodation_types': AccommodationType.objects.all(),
        # 'accommodation_by_type': get_accommodation_by_type(),
        # 'recent_allocations': Allocation.objects.order_by('-created_at')[:10],
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
    }
    return render(request, 'accommodation/reports.html', context)
