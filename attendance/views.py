from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator

# Import models (these would be created in models.py)
# from .models import Attendance, Leave, LeaveType, AttendanceStatus
# from employees.models import Employee


@login_required
def dashboard(request):
    """
    Main attendance dashboard showing attendance statistics and recent activities.
    """
    context = {
        'title': 'Attendance Dashboard',
        'today': timezone.now().date(),
        # 'present_count': Attendance.objects.filter(date=timezone.now().date(), status='present').count(),
        # 'absent_count': Attendance.objects.filter(date=timezone.now().date(), status='absent').count(),
        # 'leave_count': Attendance.objects.filter(date=timezone.now().date(), status='leave').count(),
        # 'pending_leaves': Leave.objects.filter(status='pending').count(),
        # 'recent_attendances': Attendance.objects.order_by('-date', '-time_in')[:10],
    }
    return render(request, 'attendance/dashboard.html', context)


@login_required
def mark_attendance(request):
    """
    View for marking attendance for an individual employee or self.
    """
    if request.method == 'POST':
        # Process the attendance form
        # employee_id = request.POST.get('employee_id')
        # status = request.POST.get('status')
        # date = request.POST.get('date', timezone.now().date())
        # time_in = request.POST.get('time_in', timezone.now().time())
        # time_out = request.POST.get('time_out')
        # remarks = request.POST.get('remarks', '')
        
        # Create attendance record
        # attendance = Attendance.objects.create(...)
        
        messages.success(request, "Attendance marked successfully.")
        return redirect('attendance:dashboard')
    
    context = {
        'title': 'Mark Attendance',
        'today': timezone.now().date(),
        # 'employees': Employee.objects.filter(is_active=True),
        # 'attendance_statuses': AttendanceStatus.choices,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
@staff_member_required
def mark_attendance_bulk(request):
    """
    View for marking attendance in bulk for multiple employees.
    """
    if request.method == 'POST':
        # Process the bulk attendance form
        # date = request.POST.get('date', timezone.now().date())
        # employee_ids = request.POST.getlist('employee_ids')
        # statuses = request.POST.getlist('statuses')
        
        # Create attendance records in bulk
        # for i, employee_id in enumerate(employee_ids):
        #     status = statuses[i]
        #     Attendance.objects.create(...)
        
        messages.success(request, "Bulk attendance marked successfully.")
        return redirect('attendance:dashboard')
    
    context = {
        'title': 'Mark Bulk Attendance',
        'today': timezone.now().date(),
        # 'employees': Employee.objects.filter(is_active=True),
        # 'attendance_statuses': AttendanceStatus.choices,
    }
    return render(request, 'attendance/mark_attendance_bulk.html', context)


@login_required
def leave_list(request):
    """
    View to display list of leave requests with filtering options.
    """
    # Get filter parameters
    # status = request.GET.get('status')
    # leave_type = request.GET.get('leave_type')
    # from_date = request.GET.get('from_date')
    # to_date = request.GET.get('to_date')
    
    # Base queryset
    # leaves = Leave.objects.all()
    
    # Apply filters
    # if status:
    #     leaves = leaves.filter(status=status)
    # if leave_type:
    #     leaves = leaves.filter(leave_type=leave_type)
    # if from_date:
    #     leaves = leaves.filter(start_date__gte=from_date)
    # if to_date:
    #     leaves = leaves.filter(end_date__lte=to_date)
    
    # Check if user is staff
    if not request.user.is_staff:
        # Show only the user's leaves
        # leaves = leaves.filter(employee=request.user.employee_profile)
        pass
    
    # Pagination
    # paginator = Paginator(leaves, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Leave Requests',
        # 'page_obj': page_obj,
        # 'leave_types': LeaveType.objects.all(),
        # 'status_choices': Leave.STATUS_CHOICES,
    }
    return render(request, 'attendance/leave_list.html', context)


@login_required
def leave_apply(request):
    """
    View for an employee to apply for leave.
    """
    if request.method == 'POST':
        # Process the leave application form
        # leave_type_id = request.POST.get('leave_type')
        # start_date = request.POST.get('start_date')
        # end_date = request.POST.get('end_date')
        # reason = request.POST.get('reason')
        # contact_during_leave = request.POST.get('contact_during_leave')
        
        # Create leave request
        # leave = Leave.objects.create(
        #     employee=request.user.employee_profile,
        #     leave_type_id=leave_type_id,
        #     start_date=start_date,
        #     end_date=end_date,
        #     reason=reason,
        #     contact_during_leave=contact_during_leave,
        #     status='pending'
        # )
        
        messages.success(request, "Leave application submitted successfully.")
        return redirect('attendance:leaves')
    
    context = {
        'title': 'Apply for Leave',
        # 'leave_types': LeaveType.objects.all(),
        # 'leave_balance': get_leave_balance(request.user.employee_profile),
    }
    return render(request, 'attendance/leave_apply.html', context)


@login_required
def leave_detail(request, leave_id):
    """
    View to see details of a specific leave request.
    """
    # leave = get_object_or_404(Leave, pk=leave_id)
    
    # Check if user has permission to view this leave
    # if not request.user.is_staff and request.user.employee_profile != leave.employee:
    #     messages.error(request, "You don't have permission to view this leave request.")
    #     return redirect('attendance:leaves')
    
    context = {
        'title': 'Leave Request Details',
        # 'leave': leave,
    }
    return render(request, 'attendance/leave_detail.html', context)


@login_required
@staff_member_required
def leave_approve(request, leave_id):
    """
    View to approve a leave request.
    """
    # leave = get_object_or_404(Leave, pk=leave_id)
    # leave.status = 'approved'
    # leave.approved_by = request.user
    # leave.approved_date = timezone.now()
    # leave.save()
    
    messages.success(request, "Leave request approved successfully.")
    return redirect('attendance:leave_detail', leave_id=leave_id)


@login_required
@staff_member_required
def leave_reject(request, leave_id):
    """
    View to reject a leave request.
    """
    # leave = get_object_or_404(Leave, pk=leave_id)
    # leave.status = 'rejected'
    # leave.rejected_by = request.user
    # leave.rejected_date = timezone.now()
    # leave.rejection_reason = request.POST.get('rejection_reason', '')
    # leave.save()
    
    messages.success(request, "Leave request rejected successfully.")
    return redirect('attendance:leave_detail', leave_id=leave_id)


@login_required
@staff_member_required
def attendance_reports(request):
    """
    View for attendance reports and analytics.
    """
    context = {
        'title': 'Attendance Reports',
        # 'departments': Department.objects.all(),
        # 'total_employees': Employee.objects.filter(is_active=True).count(),
        # 'attendance_summary': get_attendance_summary(),
    }
    return render(request, 'attendance/reports.html', context)


@login_required
@staff_member_required
def monthly_report(request):
    """
    View for monthly attendance report.
    """
    # Get filter parameters
    # month = request.GET.get('month', timezone.now().month)
    # year = request.GET.get('year', timezone.now().year)
    # department_id = request.GET.get('department')
    
    # Generate report data
    # report_data = generate_monthly_report(month, year, department_id)
    
    context = {
        'title': 'Monthly Attendance Report',
        # 'report_data': report_data,
        # 'month': month,
        # 'year': year,
        # 'departments': Department.objects.all(),
        # 'selected_department': department_id,
    }
    return render(request, 'attendance/monthly_report.html', context)


@login_required
def employee_report(request, employee_id):
    """
    View for individual employee attendance report.
    """
    # employee = get_object_or_404(Employee, pk=employee_id)
    
    # Check if user has permission to view this report
    # if not request.user.is_staff and request.user.employee_profile.id != employee_id:
    #     messages.error(request, "You don't have permission to view this report.")
    #     return redirect('attendance:reports')
    
    # Get filter parameters
    # month = request.GET.get('month', timezone.now().month)
    # year = request.GET.get('year', timezone.now().year)
    
    # Generate report data
    # report_data = generate_employee_report(employee, month, year)
    
    context = {
        'title': f'Attendance Report: Employee',  # Would include employee name
        # 'employee': employee,
        # 'report_data': report_data,
        # 'month': month,
        # 'year': year,
        # 'attendance_summary': get_employee_attendance_summary(employee),
    }
    return render(request, 'attendance/employee_report.html', context)


@login_required
def api_attendance_status(request):
    """
    API endpoint to get attendance status for the current day.
    """
    # employee = request.user.employee_profile
    # today = timezone.now().date()
    
    # try:
    #     attendance = Attendance.objects.get(employee=employee, date=today)
    #     status = attendance.status
    #     time_in = attendance.time_in
    #     time_out = attendance.time_out
    # except Attendance.DoesNotExist:
    #     status = 'not_marked'
    #     time_in = None
    #     time_out = None
    
    data = {
        'status': 'present',  # Placeholder value
        'date': timezone.now().date().isoformat(),
        'time_in': timezone.now().time().isoformat(),
        'time_out': None,
    }
    return JsonResponse(data)
