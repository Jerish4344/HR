from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import (
    Company, Department, Store, Role, SystemConfig, 
    Notification, ActivityLog, Document
)

from employees.models import Employee, EmployeeStatus
from attendance.models import Attendance, Leave
from payroll.models import Salary, PayrollProcessing
from accommodation.models import Accommodation, MaintenanceRequest
from tracking.models import EmployeeTracking
from reports.models import Report

import json
from datetime import datetime, timedelta
from calendar import monthrange


def index(request):
    """
    Landing page view - shown before login
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Get company information to display on landing page
    try:
        company = Company.objects.filter(is_active=True).first()
    except:
        company = None
    
    context = {
        'company': company,
        'title': 'Welcome to HR Management System'
    }
    return render(request, 'core/index.html', context)


@login_required
def dashboard(request):
    """
    Main dashboard view - shown after login
    """
    # Get current user's employee profile
    try:
        employee = request.user.employee_profile
    except:
        employee = None
    
    # Get basic stats for dashboard widgets
    total_employees = Employee.objects.filter(is_deleted=False).count()
    active_employees = Employee.objects.filter(
        is_deleted=False, 
        status=EmployeeStatus.ACTIVE
    ).count()
    
    # Get department distribution
    departments = Department.objects.filter(is_active=True)
    dept_employee_counts = []
    for dept in departments[:5]:  # Limit to top 5 departments
        count = Employee.objects.filter(
            department=dept, 
            is_deleted=False
        ).count()
        dept_employee_counts.append({
            'name': dept.name,
            'count': count
        })
    
    # Get recent notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Get today's attendance stats
    today = timezone.now().date()
    try:
        today_attendance = Attendance.objects.filter(date=today).aggregate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            half_day=Count('id', filter=Q(status='half_day'))
        )
    except:
        today_attendance = {'present': 0, 'absent': 0, 'late': 0, 'half_day': 0}
    
    # Get pending leave requests (for managers)
    pending_leaves = 0
    if employee and employee.is_manager():
        try:
            pending_leaves = Leave.objects.filter(
                status='pending',
                employee__reporting_manager=employee
            ).count()
        except:
            pending_leaves = 0
    
    # Get maintenance requests (for admin/HR)
    pending_maintenance = 0
    if request.user.is_staff:
        try:
            pending_maintenance = MaintenanceRequest.objects.filter(
                status='pending'
            ).count()
        except:
            pending_maintenance = 0
    
    context = {
        'title': 'Dashboard',
        'employee': employee,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'dept_employee_counts': dept_employee_counts,
        'notifications': notifications,
        'notification_count': notifications.count(),
        'today_attendance': today_attendance,
        'pending_leaves': pending_leaves,
        'pending_maintenance': pending_maintenance,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    """
    User profile view
    """
    try:
        employee = request.user.employee_profile
    except:
        messages.error(request, "Employee profile not found.")
        return redirect('core:dashboard')
    
    # Get employee documents
    documents = employee.get_documents()
    
    # Get attendance summary for current month
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    
    try:
        attendance_summary = Attendance.objects.filter(
            employee=employee,
            date__range=[first_day, last_day]
        ).aggregate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            half_day=Count('id', filter=Q(status='half_day'))
        )
    except:
        attendance_summary = {'present': 0, 'absent': 0, 'late': 0, 'half_day': 0}
    
    # Get leave balance
    try:
        leave_balance = Leave.objects.filter(
            employee=employee,
            year=today.year
        ).aggregate(
            total_casual=Sum('casual_leave_balance'),
            total_sick=Sum('sick_leave_balance'),
            total_earned=Sum('earned_leave_balance')
        )
    except:
        leave_balance = {'total_casual': 0, 'total_sick': 0, 'total_earned': 0}
    
    context = {
        'title': 'My Profile',
        'employee': employee,
        'documents': documents,
        'attendance_summary': attendance_summary,
        'leave_balance': leave_balance
    }
    
    return render(request, 'core/profile.html', context)


@login_required
def edit_profile(request):
    """
    Edit user profile view
    """
    try:
        employee = request.user.employee_profile
    except:
        messages.error(request, "Employee profile not found.")
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Update basic contact information
        employee.primary_phone = request.POST.get('primary_phone', employee.primary_phone)
        employee.secondary_phone = request.POST.get('secondary_phone', employee.secondary_phone)
        employee.personal_email = request.POST.get('personal_email', employee.personal_email)
        
        # Update profile picture if provided
        if 'profile_picture' in request.FILES:
            employee.profile_picture = request.FILES['profile_picture']
        
        # Update user password if provided
        if request.POST.get('new_password'):
            if request.user.check_password(request.POST.get('current_password', '')):
                request.user.set_password(request.POST.get('new_password'))
                request.user.save()
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Current password is incorrect.")
        
        employee.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('core:profile')
    
    context = {
        'title': 'Edit Profile',
        'employee': employee
    }
    
    return render(request, 'core/edit_profile.html', context)


@login_required
def help_page(request):
    """
    Help and documentation page
    """
    # Get help topics from system config
    try:
        help_topics = SystemConfig.objects.filter(
            key__startswith='help_',
            is_public=True
        )
    except:
        help_topics = []
    
    context = {
        'title': 'Help & Documentation',
        'help_topics': help_topics
    }
    
    return render(request, 'core/help.html', context)


@staff_member_required
def system_settings(request):
    """
    System settings page (admin only)
    """
    if request.method == 'POST':
        # Update system settings
        for key, value in request.POST.items():
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                try:
                    config = SystemConfig.objects.get(key=config_key)
                    config.value = value
                    config.updated_by = request.user
                    config.save()
                except SystemConfig.DoesNotExist:
                    pass
        
        messages.success(request, "System settings updated successfully.")
        return redirect('core:settings')
    
    # Get all system configurations
    configs = SystemConfig.objects.all().order_by('key')
    
    context = {
        'title': 'System Settings',
        'configs': configs
    }
    
    return render(request, 'core/settings.html', context)


@login_required
def notifications(request):
    """
    User notifications page
    """
    # Get all notifications for the user
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate notifications
    paginator = Paginator(all_notifications, 20)  # Show 20 notifications per page
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    # Mark notifications as read if requested
    if request.GET.get('mark_read') == 'all':
        all_notifications.update(is_read=True, read_at=timezone.now())
        messages.success(request, "All notifications marked as read.")
        return redirect('core:notifications')
    
    context = {
        'title': 'Notifications',
        'notifications': notifications,
        'unread_count': all_notifications.filter(is_read=False).count()
    }
    
    return render(request, 'core/notifications.html', context)


@login_required
def dashboard_stats(request):
    """
    API endpoint for dashboard widgets
    Returns JSON data for dashboard charts and widgets
    """
    stats = {}
    
    # Get date range for stats
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Employee statistics
    try:
        employee_stats = {
            'total': Employee.objects.filter(is_deleted=False).count(),
            'active': Employee.objects.filter(is_deleted=False, status=EmployeeStatus.ACTIVE).count(),
            'on_leave': Employee.objects.filter(is_deleted=False, status=EmployeeStatus.ON_LEAVE).count(),
            'new_hires': Employee.objects.filter(
                is_deleted=False, 
                date_joined__gte=start_date
            ).count(),
            'by_department': []
        }
        
        # Get department distribution
        departments = Department.objects.filter(is_active=True)
        for dept in departments:
            count = Employee.objects.filter(department=dept, is_deleted=False).count()
            if count > 0:
                employee_stats['by_department'].append({
                    'name': dept.name,
                    'count': count
                })
        
        stats['employees'] = employee_stats
    except:
        stats['employees'] = {
            'total': 0,
            'active': 0,
            'on_leave': 0,
            'new_hires': 0,
            'by_department': []
        }
    
    # Attendance statistics
    try:
        attendance_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_stats = Attendance.objects.filter(date=current_date).aggregate(
                present=Count('id', filter=Q(status='present')),
                absent=Count('id', filter=Q(status='absent')),
                late=Count('id', filter=Q(status='late'))
            )
            
            attendance_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'present': daily_stats['present'],
                'absent': daily_stats['absent'],
                'late': daily_stats['late']
            })
            
            current_date += timedelta(days=1)
        
        stats['attendance'] = {
            'daily_data': attendance_data,
            'summary': Attendance.objects.filter(
                date__range=[start_date, end_date]
            ).aggregate(
                present=Count('id', filter=Q(status='present')),
                absent=Count('id', filter=Q(status='absent')),
                late=Count('id', filter=Q(status='late')),
                half_day=Count('id', filter=Q(status='half_day'))
            )
        }
    except:
        stats['attendance'] = {
            'daily_data': [],
            'summary': {'present': 0, 'absent': 0, 'late': 0, 'half_day': 0}
        }
    
    # Payroll statistics
    try:
        # Get monthly payroll totals
        payroll_data = []
        for i in range(6):  # Last 6 months
            month_date = end_date.replace(day=1) - timedelta(days=i*30)
            month_name = month_date.strftime('%B %Y')
            
            monthly_total = PayrollProcessing.objects.filter(
                month=month_date.month,
                year=month_date.year,
                status='completed'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            payroll_data.append({
                'month': month_name,
                'total': float(monthly_total)
            })
        
        stats['payroll'] = {
            'monthly_data': list(reversed(payroll_data)),
            'current_month_total': PayrollProcessing.objects.filter(
                month=end_date.month,
                year=end_date.year
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
        }
    except:
        stats['payroll'] = {
            'monthly_data': [],
            'current_month_total': 0
        }
    
    # Accommodation statistics
    try:
        accommodation_stats = {
            'total_units': Accommodation.objects.count(),
            'occupied_units': Accommodation.objects.filter(status='occupied').count(),
            'maintenance_requests': {
                'pending': MaintenanceRequest.objects.filter(status='pending').count(),
                'in_progress': MaintenanceRequest.objects.filter(status='in_progress').count(),
                'completed': MaintenanceRequest.objects.filter(
                    status='completed',
                    completed_date__gte=start_date
                ).count()
            }
        }
        
        stats['accommodation'] = accommodation_stats
    except:
        stats['accommodation'] = {
            'total_units': 0,
            'occupied_units': 0,
            'maintenance_requests': {'pending': 0, 'in_progress': 0, 'completed': 0}
        }
    
    # Location tracking statistics
    try:
        tracking_stats = {
            'active_trackers': EmployeeTracking.objects.filter(
                is_active=True
            ).count(),
            'last_24h_updates': EmployeeTracking.objects.filter(
                last_update__gte=timezone.now() - timedelta(hours=24)
            ).count()
        }
        
        stats['tracking'] = tracking_stats
    except:
        stats['tracking'] = {
            'active_trackers': 0,
            'last_24h_updates': 0
        }
    
    # Log this activity
    try:
        ActivityLog.objects.create(
            user=request.user,
            activity='Viewed dashboard statistics',
            module='core',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    except:
        pass
    
    return JsonResponse(stats)
