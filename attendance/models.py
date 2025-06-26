from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, SoftDeleteModel
from employees.models import Employee


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', _('Present')
    ABSENT = 'absent', _('Absent')
    LATE = 'late', _('Late')
    HALF_DAY = 'half_day', _('Half Day')
    ON_LEAVE = 'on_leave', _('On Leave')
    HOLIDAY = 'holiday', _('Holiday')
    WEEKEND = 'weekend', _('Weekend')


class AttendanceSource(models.TextChoices):
    WEB = 'web', _('Web')
    MOBILE = 'mobile', _('Mobile App')
    BIOMETRIC = 'biometric', _('Biometric')
    MANUAL = 'manual', _('Manual Entry')
    QR_CODE = 'qr_code', _('QR Code')
    RFID = 'rfid', _('RFID Card')


class Attendance(TimeStampedModel):
    """
    Model to track daily attendance records for employees.
    """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='attendance_records'
    )
    date = models.DateField()
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.ABSENT
    )
    source = models.CharField(
        max_length=20,
        choices=AttendanceSource.choices,
        default=AttendanceSource.WEB
    )
    work_shift = models.ForeignKey(
        'WorkShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records'
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        help_text=_("Latitude coordinate for check-in location")
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        help_text=_("Longitude coordinate for check-in location")
    )
    check_out_latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        help_text=_("Latitude coordinate for check-out location")
    )
    check_out_longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        help_text=_("Longitude coordinate for check-out location")
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_attendance'
    )
    
    class Meta:
        ordering = ['-date', '-check_in_time']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"
    
    @property
    def working_hours(self):
        """Calculate the working hours for this attendance record."""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    @property
    def is_late(self):
        """Check if the employee was late based on their work shift."""
        if not self.check_in_time or not self.work_shift:
            return False
        
        # Convert datetime to time for comparison
        check_in_time = self.check_in_time.time()
        
        # Get the grace period from system settings or use default
        from core.models import SystemConfig
        try:
            grace_period = int(SystemConfig.objects.get(key='attendance_grace_period').get_typed_value())
        except (SystemConfig.DoesNotExist, ValueError):
            grace_period = 15  # Default grace period in minutes
        
        # Add grace period to shift start time
        import datetime
        grace_minutes = datetime.timedelta(minutes=grace_period)
        shift_start_with_grace = (
            datetime.datetime.combine(datetime.date.today(), self.work_shift.start_time) + 
            grace_minutes
        ).time()
        
        return check_in_time > shift_start_with_grace
    
    def mark_present(self, check_in_time=None):
        """Mark the employee as present with the given check-in time."""
        if check_in_time is None:
            check_in_time = timezone.now()
        
        self.check_in_time = check_in_time
        self.status = AttendanceStatus.PRESENT
        self.save()
    
    def mark_checkout(self, check_out_time=None):
        """Record the check-out time for the employee."""
        if check_out_time is None:
            check_out_time = timezone.now()
        
        self.check_out_time = check_out_time
        self.save()


class LeaveType(models.TextChoices):
    CASUAL = 'casual', _('Casual Leave')
    SICK = 'sick', _('Sick Leave')
    EARNED = 'earned', _('Earned Leave')
    MATERNITY = 'maternity', _('Maternity Leave')
    PATERNITY = 'paternity', _('Paternity Leave')
    UNPAID = 'unpaid', _('Unpaid Leave')
    COMP_OFF = 'comp_off', _('Compensatory Off')
    BEREAVEMENT = 'bereavement', _('Bereavement Leave')
    OTHER = 'other', _('Other')


class LeaveStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')
    CANCELLED = 'cancelled', _('Cancelled')


class Leave(TimeStampedModel, SoftDeleteModel):
    """
    Model to manage employee leave requests.
    """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='leaves'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.CASUAL
    )
    start_date = models.DateField()
    end_date = models.DateField()
    half_day = models.BooleanField(
        default=False,
        help_text=_("Whether this is a half-day leave")
    )
    first_half = models.BooleanField(
        default=True,
        help_text=_("If half day, is it first half of the day?")
    )
    num_days = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        help_text=_("Number of leave days")
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING
    )
    approver = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    attachments = models.ManyToManyField(
        'core.Document',
        blank=True,
        related_name='leave_attachments'
    )
    year = models.PositiveIntegerField(
        default=timezone.now().year,
        help_text=_("Calendar year for leave accounting")
    )
    casual_leave_balance = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Casual leave balance after this leave")
    )
    sick_leave_balance = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Sick leave balance after this leave")
    )
    earned_leave_balance = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Earned leave balance after this leave")
    )
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'start_date']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['year']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        # Calculate number of days if not provided
        if not self.num_days:
            from datetime import timedelta
            delta = (self.end_date - self.start_date).days + 1
            
            # Adjust for half day
            if self.half_day and delta == 1:
                self.num_days = 0.5
            else:
                self.num_days = delta
        
        super().save(*args, **kwargs)
    
    def approve(self, approver):
        """Approve the leave request."""
        self.status = LeaveStatus.APPROVED
        self.approver = approver
        self.approved_at = timezone.now()
        self.save()
        
        # Update attendance records for the leave period
        self._update_attendance_records()
    
    def reject(self, approver, reason):
        """Reject the leave request."""
        self.status = LeaveStatus.REJECTED
        self.approver = approver
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def cancel(self):
        """Cancel the leave request."""
        self.status = LeaveStatus.CANCELLED
        self.save()
        
        # Remove attendance records marked as on leave
        if self.status == LeaveStatus.APPROVED:
            Attendance.objects.filter(
                employee=self.employee,
                date__range=[self.start_date, self.end_date],
                status=AttendanceStatus.ON_LEAVE
            ).update(status=AttendanceStatus.ABSENT)
    
    def _update_attendance_records(self):
        """Update attendance records for the approved leave period."""
        from datetime import timedelta
        
        current_date = self.start_date
        while current_date <= self.end_date:
            # Skip weekends and holidays if needed
            is_weekend = current_date.weekday() >= 5  # 5 = Saturday, 6 = Sunday
            is_holiday = Holiday.objects.filter(date=current_date).exists()
            
            if not is_weekend and not is_holiday:
                # Create or update attendance record
                attendance, created = Attendance.objects.get_or_create(
                    employee=self.employee,
                    date=current_date,
                    defaults={
                        'status': AttendanceStatus.ON_LEAVE,
                        'notes': f"On {self.get_leave_type_display()}"
                    }
                )
                
                if not created:
                    attendance.status = AttendanceStatus.ON_LEAVE
                    attendance.notes = f"On {self.get_leave_type_display()}"
                    attendance.save()
            
            current_date += timedelta(days=1)


class LeaveBalance(TimeStampedModel):
    """
    Model to track employee leave balances for each year.
    """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='leave_balances'
    )
    year = models.PositiveIntegerField(
        default=timezone.now().year,
        help_text=_("Calendar year for leave accounting")
    )
    casual_leave_total = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Total casual leave allocated for the year")
    )
    casual_leave_used = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Casual leave used in the year")
    )
    sick_leave_total = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Total sick leave allocated for the year")
    )
    sick_leave_used = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Sick leave used in the year")
    )
    earned_leave_total = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Total earned leave allocated for the year")
    )
    earned_leave_used = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Earned leave used in the year")
    )
    carried_forward = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        default=0,
        help_text=_("Leave carried forward from previous year")
    )
    
    class Meta:
        unique_together = ['employee', 'year']
        ordering = ['-year']
        indexes = [
            models.Index(fields=['employee', 'year']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - Leave Balance {self.year}"
    
    @property
    def casual_leave_balance(self):
        """Calculate casual leave balance."""
        return self.casual_leave_total - self.casual_leave_used
    
    @property
    def sick_leave_balance(self):
        """Calculate sick leave balance."""
        return self.sick_leave_total - self.sick_leave_used
    
    @property
    def earned_leave_balance(self):
        """Calculate earned leave balance."""
        return self.earned_leave_total - self.earned_leave_used
    
    @property
    def total_balance(self):
        """Calculate total leave balance."""
        return self.casual_leave_balance + self.sick_leave_balance + self.earned_leave_balance


class HolidayType(models.TextChoices):
    NATIONAL = 'national', _('National Holiday')
    REGIONAL = 'regional', _('Regional Holiday')
    COMPANY = 'company', _('Company Holiday')
    OPTIONAL = 'optional', _('Optional Holiday')


class Holiday(TimeStampedModel):
    """
    Model to maintain the holiday calendar.
    """
    name = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.NATIONAL
    )
    is_recurring = models.BooleanField(
        default=False,
        help_text=_("Whether this holiday occurs every year on the same date")
    )
    applicable_regions = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of regions where this holiday is applicable")
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['holiday_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date.strftime('%d %b %Y')}"
    
    @classmethod
    def get_holidays_for_year(cls, year):
        """Get all holidays for a specific year."""
        start_date = timezone.datetime(year, 1, 1).date()
        end_date = timezone.datetime(year, 12, 31).date()
        
        return cls.objects.filter(
            date__range=[start_date, end_date],
            is_active=True
        )
    
    @classmethod
    def is_holiday(cls, date):
        """Check if a given date is a holiday."""
        return cls.objects.filter(date=date, is_active=True).exists()


class WorkShift(TimeStampedModel, SoftDeleteModel):
    """
    Model to define different work shifts.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.PositiveIntegerField(
        default=60,
        help_text=_("Break duration in minutes")
    )
    working_days = models.JSONField(
        default=list,
        help_text=_("List of working days (0=Monday, 6=Sunday)")
    )
    description = models.TextField(blank=True, null=True)
    is_night_shift = models.BooleanField(
        default=False,
        help_text=_("Whether this is a night shift")
    )
    grace_period = models.PositiveIntegerField(
        default=15,
        help_text=_("Grace period in minutes for late arrival")
    )
    early_exit_limit = models.PositiveIntegerField(
        default=15,
        help_text=_("Early exit limit in minutes")
    )
    minimum_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=8.0,
        help_text=_("Minimum working hours required")
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    @property
    def duration_hours(self):
        """Calculate the duration of the shift in hours."""
        import datetime
        
        start_datetime = datetime.datetime.combine(datetime.date.today(), self.start_time)
        end_datetime = datetime.datetime.combine(datetime.date.today(), self.end_time)
        
        # Handle overnight shifts
        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)
        
        delta = end_datetime - start_datetime
        total_minutes = delta.total_seconds() / 60
        
        # Subtract break duration
        working_minutes = total_minutes - self.break_duration
        
        return round(working_minutes / 60, 2)
    
    @property
    def formatted_working_days(self):
        """Return formatted string of working days."""
        days_map = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }
        
        return ', '.join([days_map.get(day, '') for day in self.working_days])
    
    def is_working_day(self, date):
        """Check if a given date is a working day for this shift."""
        return date.weekday() in self.working_days


class AttendanceCorrection(TimeStampedModel):
    """
    Model to track attendance correction requests.
    """
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='corrections'
    )
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_correction_requests'
    )
    original_check_in = models.DateTimeField(null=True, blank=True)
    original_check_out = models.DateTimeField(null=True, blank=True)
    requested_check_in = models.DateTimeField(null=True, blank=True)
    requested_check_out = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,  # Reusing leave status choices
        default=LeaveStatus.PENDING
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_corrections'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Correction for {self.attendance.employee.full_name} on {self.attendance.date}"
    
    def approve(self, approver):
        """Approve the correction request and update the attendance record."""
        self.status = LeaveStatus.APPROVED
        self.approver = approver
        self.approved_at = timezone.now()
        
        # Update the attendance record
        if self.requested_check_in:
            self.attendance.check_in_time = self.requested_check_in
        
        if self.requested_check_out:
            self.attendance.check_out_time = self.requested_check_out
        
        # Update attendance status if needed
        if self.attendance.check_in_time and not self.attendance.status == AttendanceStatus.ON_LEAVE:
            self.attendance.status = AttendanceStatus.PRESENT
        
        self.attendance.save()
        self.save()
    
    def reject(self, approver, reason):
        """Reject the correction request."""
        self.status = LeaveStatus.REJECTED
        self.approver = approver
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()
