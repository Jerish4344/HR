from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Import models (these would be created in models.py)
# from .models import EmployeeTracking, GeofenceArea, DeviceInfo, TrackingLog
# from employees.models import Employee
# from core.models import Store


@login_required
def dashboard(request):
    """
    Main tracking dashboard showing real-time location of employees and statistics.
    """
    context = {
        'title': 'Tracking Dashboard',
        # 'active_tracking_count': EmployeeTracking.objects.filter(is_active=True).count(),
        # 'geofence_count': GeofenceArea.objects.filter(is_active=True).count(),
        # 'device_count': DeviceInfo.objects.filter(is_active=True).count(),
        # 'recently_tracked': EmployeeTracking.objects.filter(is_active=True).order_by('-last_update')[:10],
    }
    return render(request, 'tracking/dashboard.html', context)


@login_required
@staff_member_required
def view(request):
    """
    View for displaying the real-time tracking map with all active employees.
    """
    # Get filter parameters
    # department_id = request.GET.get('department')
    # store_id = request.GET.get('store')
    # geofence_id = request.GET.get('geofence')
    
    # Base queryset
    # tracking_data = EmployeeTracking.objects.filter(is_active=True)
    
    # Apply filters
    # if department_id:
    #     tracking_data = tracking_data.filter(employee__department_id=department_id)
    # if store_id:
    #     tracking_data = tracking_data.filter(current_store_id=store_id)
    # if geofence_id:
    #     tracking_data = tracking_data.filter(current_geofence_id=geofence_id)
    
    context = {
        'title': 'Track Employees',
        # 'tracking_data': tracking_data,
        # 'departments': Department.objects.filter(is_active=True),
        # 'stores': Store.objects.filter(is_active=True),
        # 'geofences': GeofenceArea.objects.filter(is_active=True),
        # 'map_center': calculate_map_center(tracking_data),
    }
    return render(request, 'tracking/view.html', context)


@login_required
def employee_tracking(request, employee_id):
    """
    View to display tracking details for a specific employee.
    """
    # employee = get_object_or_404(Employee, pk=employee_id, is_deleted=False)
    
    # Check if user has permission to view this employee's tracking
    # if not request.user.is_staff and request.user.employee_profile != employee:
    #     if not hasattr(request.user, 'employee_profile') or employee.reporting_manager != request.user.employee_profile:
    #         messages.error(request, "You don't have permission to view this employee's tracking data.")
    #         return redirect('tracking:dashboard')
    
    # Get tracking data
    # tracking = EmployeeTracking.objects.filter(employee=employee).first()
    
    # Get date range for history
    # start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).date())
    # end_date = request.GET.get('end_date', timezone.now().date())
    
    # Get tracking logs
    # tracking_logs = TrackingLog.objects.filter(
    #     employee=employee,
    #     timestamp__date__gte=start_date,
    #     timestamp__date__lte=end_date
    # ).order_by('-timestamp')
    
    context = {
        'title': f'Tracking: Employee',  # Would include employee name
        # 'employee': employee,
        # 'tracking': tracking,
        # 'tracking_logs': tracking_logs,
        # 'start_date': start_date,
        # 'end_date': end_date,
    }
    return render(request, 'tracking/employee_tracking.html', context)


@login_required
@staff_member_required
def geofence_list(request):
    """
    View to display list of geofences with filtering options.
    """
    # Get filter parameters
    # status = request.GET.get('status')
    # store_id = request.GET.get('store')
    # geofence_type = request.GET.get('type')
    
    # Base queryset
    # geofences = GeofenceArea.objects.filter(is_deleted=False)
    
    # Apply filters
    # if status:
    #     is_active = status == 'active'
    #     geofences = geofences.filter(is_active=is_active)
    # if store_id:
    #     geofences = geofences.filter(store_id=store_id)
    # if geofence_type:
    #     geofences = geofences.filter(geofence_type=geofence_type)
    
    # Pagination
    # paginator = Paginator(geofences, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Geofences',
        # 'page_obj': page_obj,
        # 'stores': Store.objects.filter(is_active=True),
        # 'geofence_types': GeofenceType.choices,
    }
    return render(request, 'tracking/geofence_list.html', context)


@login_required
@staff_member_required
def add_geofence(request):
    """
    View to add a new geofence.
    """
    if request.method == 'POST':
        # Process the geofence form
        # name = request.POST.get('name')
        # description = request.POST.get('description')
        # geofence_type = request.POST.get('geofence_type')
        # store_id = request.POST.get('store')
        # is_active = request.POST.get('is_active') == 'on'
        # color = request.POST.get('color', '#3388ff')
        
        # Process geofence coordinates based on type
        # if geofence_type == 'circle':
        #     center_latitude = request.POST.get('center_latitude')
        #     center_longitude = request.POST.get('center_longitude')
        #     radius = request.POST.get('radius')
        #     
        #     geofence = GeofenceArea.objects.create(
        #         name=name,
        #         description=description,
        #         geofence_type=geofence_type,
        #         center_latitude=center_latitude,
        #         center_longitude=center_longitude,
        #         radius=radius,
        #         store_id=store_id,
        #         is_active=is_active,
        #         color=color,
        #         created_by=request.user,
        #         updated_by=request.user
        #     )
        # else:
        #     # For polygon or rectangle
        #     coordinates = json.loads(request.POST.get('coordinates', '[]'))
        #     
        #     geofence = GeofenceArea.objects.create(
        #         name=name,
        #         description=description,
        #         geofence_type=geofence_type,
        #         coordinates=coordinates,
        #         store_id=store_id,
        #         is_active=is_active,
        #         color=color,
        #         created_by=request.user,
        #         updated_by=request.user
        #     )
        
        messages.success(request, "Geofence added successfully.")
        return redirect('tracking:geofence_list')
    
    context = {
        'title': 'Add Geofence',
        # 'stores': Store.objects.filter(is_active=True),
        # 'geofence_types': GeofenceType.choices,
    }
    return render(request, 'tracking/geofence_form.html', context)


@login_required
@staff_member_required
def geofence_detail(request, geofence_id):
    """
    View to see details of a specific geofence.
    """
    # geofence = get_object_or_404(GeofenceArea, pk=geofence_id, is_deleted=False)
    
    # Get employees currently in this geofence
    # current_employees = EmployeeTracking.objects.filter(current_geofence=geofence, is_active=True)
    
    context = {
        'title': 'Geofence Details',
        # 'geofence': geofence,
        # 'current_employees': current_employees,
        # 'tracking_logs': TrackingLog.objects.filter(geofence=geofence).order_by('-timestamp')[:50],
    }
    return render(request, 'tracking/geofence_detail.html', context)


@login_required
@staff_member_required
def edit_geofence(request, geofence_id):
    """
    View to edit an existing geofence.
    """
    # geofence = get_object_or_404(GeofenceArea, pk=geofence_id, is_deleted=False)
    
    if request.method == 'POST':
        # Process the geofence form
        # geofence.name = request.POST.get('name')
        # geofence.description = request.POST.get('description')
        # geofence.store_id = request.POST.get('store')
        # geofence.is_active = request.POST.get('is_active') == 'on'
        # geofence.color = request.POST.get('color', '#3388ff')
        # geofence.updated_by = request.user
        
        # Process geofence coordinates based on type
        # if geofence.geofence_type == 'circle':
        #     geofence.center_latitude = request.POST.get('center_latitude')
        #     geofence.center_longitude = request.POST.get('center_longitude')
        #     geofence.radius = request.POST.get('radius')
        # else:
        #     # For polygon or rectangle
        #     geofence.coordinates = json.loads(request.POST.get('coordinates', '[]'))
        
        # geofence.save()
        
        messages.success(request, "Geofence updated successfully.")
        return redirect('tracking:geofence_detail', geofence_id=geofence_id)
    
    context = {
        'title': 'Edit Geofence',
        # 'geofence': geofence,
        # 'stores': Store.objects.filter(is_active=True),
    }
    return render(request, 'tracking/geofence_form.html', context)


@login_required
@staff_member_required
def device_list(request):
    """
    View to display list of tracking devices.
    """
    # Get filter parameters
    # status = request.GET.get('status')
    # device_type = request.GET.get('device_type')
    
    # Base queryset
    # devices = DeviceInfo.objects.all()
    
    # Apply filters
    # if status:
    #     is_active = status == 'active'
    #     devices = devices.filter(is_active=is_active)
    # if device_type:
    #     devices = devices.filter(device_type=device_type)
    
    # Pagination
    # paginator = Paginator(devices, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Tracking Devices',
        # 'page_obj': page_obj,
        # 'device_types': DeviceType.choices,
    }
    return render(request, 'tracking/device_list.html', context)


@login_required
@staff_member_required
def device_detail(request, device_id):
    """
    View to see details of a specific device.
    """
    # device = get_object_or_404(DeviceInfo, pk=device_id)
    
    context = {
        'title': 'Device Details',
        # 'device': device,
        # 'tracking_logs': TrackingLog.objects.filter(device=device).order_by('-timestamp')[:50],
    }
    return render(request, 'tracking/device_detail.html', context)


@login_required
@staff_member_required
def reports(request):
    """
    View for tracking reports and analytics.
    """
    context = {
        'title': 'Tracking Reports',
        # 'active_tracking_count': EmployeeTracking.objects.filter(is_active=True).count(),
        # 'total_devices': DeviceInfo.objects.count(),
        # 'geofence_events_today': TrackingLog.objects.filter(
        #     timestamp__date=timezone.now().date(),
        #     event_type__in=['geofence_enter', 'geofence_exit']
        # ).count(),
    }
    return render(request, 'tracking/reports.html', context)


@login_required
@staff_member_required
def location_history(request):
    """
    View for employee location history.
    """
    # Get filter parameters
    # employee_id = request.GET.get('employee')
    # start_date = request.GET.get('start_date', (timezone.now() - timezone.timedelta(days=7)).date())
    # end_date = request.GET.get('end_date', timezone.now().date())
    # event_type = request.GET.get('event_type')
    
    # Base queryset
    # logs = TrackingLog.objects.filter(
    #     timestamp__date__gte=start_date,
    #     timestamp__date__lte=end_date
    # )
    
    # Apply filters
    # if employee_id:
    #     logs = logs.filter(employee_id=employee_id)
    # if event_type:
    #     logs = logs.filter(event_type=event_type)
    
    # Order by timestamp
    # logs = logs.order_by('-timestamp')
    
    # Pagination
    # paginator = Paginator(logs, 50)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Location History',
        # 'page_obj': page_obj,
        # 'employees': Employee.objects.filter(is_active=True),
        # 'event_types': TrackingEventType.choices,
        # 'start_date': start_date,
        # 'end_date': end_date,
        # 'selected_employee': employee_id,
        # 'selected_event_type': event_type,
    }
    return render(request, 'tracking/location_history.html', context)


@csrf_exempt
@require_POST
def api_update_location(request):
    """
    API endpoint for mobile apps to update employee location.
    
    Expected POST data:
    - employee_id: ID of the employee
    - device_id: ID of the device
    - latitude: Current latitude
    - longitude: Current longitude
    - accuracy: Location accuracy in meters (optional)
    - battery_level: Device battery level percentage (optional)
    - timestamp: Timestamp of the location update (optional, defaults to now)
    """
    # Authenticate request (would normally use token authentication)
    # auth_token = request.headers.get('Authorization')
    # if not auth_token or not validate_auth_token(auth_token):
    #     return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # Get data from request
    # employee_id = request.POST.get('employee_id')
    # device_id = request.POST.get('device_id')
    # latitude = request.POST.get('latitude')
    # longitude = request.POST.get('longitude')
    # accuracy = request.POST.get('accuracy')
    # battery_level = request.POST.get('battery_level')
    # timestamp = request.POST.get('timestamp')
    
    # Validate required fields
    # if not all([employee_id, device_id, latitude, longitude]):
    #     return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    # try:
    #     employee = Employee.objects.get(pk=employee_id, is_deleted=False)
    #     device, created = DeviceInfo.objects.get_or_create(
    #         device_id=device_id,
    #         defaults={
    #             'employee': employee,
    #             'device_type': request.POST.get('device_type', 'other'),
    #             'device_model': request.POST.get('device_model'),
    #             'os_version': request.POST.get('os_version'),
    #             'app_version': request.POST.get('app_version'),
    #             'is_active': True
    #         }
    #     )
    #     
    #     # Update device info
    #     device.last_seen = timezone.now()
    #     device.save()
    #     
    #     # Get or create employee tracking
    #     tracking, created = EmployeeTracking.objects.get_or_create(
    #         employee=employee,
    #         defaults={'is_active': True}
    #     )
    #     
    #     # Update location
    #     tracking.update_location(
    #         latitude=float(latitude),
    #         longitude=float(longitude),
    #         accuracy=float(accuracy) if accuracy else None,
    #         battery_level=float(battery_level) if battery_level else None
    #     )
    #     
    #     return JsonResponse({
    #         'success': True,
    #         'tracking_id': tracking.id,
    #         'timestamp': tracking.last_update.isoformat()
    #     })
    # except Exception as e:
    #     return JsonResponse({'error': str(e)}, status=500)
    
    # Sample response for demonstration
    return JsonResponse({
        'success': True,
        'tracking_id': 123,
        'timestamp': timezone.now().isoformat()
    })


@login_required
def api_geofences(request):
    """
    API endpoint to get all active geofences.
    """
    # geofences = GeofenceArea.objects.filter(is_active=True)
    # 
    # data = []
    # for geofence in geofences:
    #     geofence_data = {
    #         'id': geofence.id,
    #         'name': geofence.name,
    #         'type': geofence.geofence_type,
    #         'color': geofence.color
    #     }
    #     
    #     if geofence.geofence_type == 'circle':
    #         geofence_data.update({
    #             'center': [float(geofence.center_latitude), float(geofence.center_longitude)],
    #             'radius': float(geofence.radius)
    #         })
    #     else:
    #         geofence_data.update({
    #             'coordinates': geofence.coordinates
    #         })
    #     
    #     data.append(geofence_data)
    
    # Sample data for demonstration
    data = [
        {
            'id': 1,
            'name': 'Office Building',
            'type': 'circle',
            'color': '#3388ff',
            'center': [12.9716, 77.5946],
            'radius': 100
        },
        {
            'id': 2,
            'name': 'Warehouse',
            'type': 'polygon',
            'color': '#ff3333',
            'coordinates': [
                [12.9716, 77.5946],
                [12.9726, 77.5956],
                [12.9736, 77.5946],
                [12.9726, 77.5936]
            ]
        }
    ]
    
    return JsonResponse({'geofences': data})


# Helper functions

def calculate_map_center(tracking_data):
    """
    Calculate the center point for the tracking map based on active employees.
    """
    # if not tracking_data.exists():
    #     # Default to a central location if no tracking data
    #     return [12.9716, 77.5946]  # Example: Bangalore coordinates
    # 
    # # Calculate average lat/lng
    # lat_sum = sum(float(t.last_latitude) for t in tracking_data if t.last_latitude)
    # lng_sum = sum(float(t.last_longitude) for t in tracking_data if t.last_longitude)
    # count = sum(1 for t in tracking_data if t.last_latitude and t.last_longitude)
    # 
    # if count > 0:
    #     return [lat_sum / count, lng_sum / count]
    # else:
    #     return [12.9716, 77.5946]  # Default
    
    # Sample data for demonstration
    return [12.9716, 77.5946]  # Example: Bangalore coordinates


def validate_auth_token(token):
    """
    Validate the authentication token from mobile app.
    """
    # This would normally check the token against a database or auth service
    # For demonstration, we'll just return True
    return True
