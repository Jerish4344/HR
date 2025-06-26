from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import TimeStampedModel, SoftDeleteModel
from employees.models import Employee


class ReportType(models.TextChoices):
    EMPLOYEE = 'employee', _('Employee')
    ATTENDANCE = 'attendance', _('Attendance')
    PAYROLL = 'payroll', _('Payroll')
    ACCOMMODATION = 'accommodation', _('Accommodation')
    TRACKING = 'tracking', _('Tracking')
    CUSTOM = 'custom', _('Custom')


class ReportFormat(models.TextChoices):
    PDF = 'pdf', _('PDF')
    EXCEL = 'excel', _('Excel')
    CSV = 'csv', _('CSV')
    HTML = 'html', _('HTML')
    JSON = 'json', _('JSON')


class ReportFrequency(models.TextChoices):
    DAILY = 'daily', _('Daily')
    WEEKLY = 'weekly', _('Weekly')
    MONTHLY = 'monthly', _('Monthly')
    QUARTERLY = 'quarterly', _('Quarterly')
    YEARLY = 'yearly', _('Yearly')
    ONCE = 'once', _('One Time')


class ReportStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    ACTIVE = 'active', _('Active')
    ARCHIVED = 'archived', _('Archived')


class Report(TimeStampedModel, SoftDeleteModel):
    """
    Model to store report definitions.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.CUSTOM
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT
    )
    data_source = models.CharField(
        max_length=100,
        help_text=_("Database table or view used as data source")
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Filter criteria for the report")
    )
    columns = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Columns to include in the report")
    )
    sorting = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Sorting configuration")
    )
    grouping = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Grouping configuration")
    )
    chart_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Chart configuration if applicable")
    )
    default_format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF
    )
    template = models.ForeignKey(
        'ReportTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    is_system = models.BooleanField(
        default=False,
        help_text=_("Whether this is a system-defined report")
    )
    is_public = models.BooleanField(
        default=False,
        help_text=_("Whether this report is accessible to all users")
    )
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Roles allowed to access this report")
    )
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='accessible_reports',
        help_text=_("Users allowed to access this report")
    )
    custom_sql = models.TextField(
        blank=True,
        null=True,
        help_text=_("Custom SQL query for advanced reports")
    )
    parameters = models.JSONField(
        default=list,
        blank=True,
        help_text=_("User-configurable parameters for the report")
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.name
    
    def generate(self, parameters=None, format=None):
        """
        Generate the report with the given parameters and format.
        
        Args:
            parameters: Dictionary of parameter values
            format: Output format (defaults to self.default_format)
            
        Returns:
            ReportData object containing the generated report
        """
        from django.db import connection
        import json
        
        # Use provided format or default
        output_format = format or self.default_format
        
        # Merge default parameters with provided ones
        merged_params = {}
        for param in self.parameters:
            param_name = param.get('name')
            if param_name:
                merged_params[param_name] = param.get('default_value')
        
        if parameters:
            merged_params.update(parameters)
        
        # Execute the appropriate query based on report type
        if self.custom_sql:
            # For custom SQL reports
            with connection.cursor() as cursor:
                cursor.execute(self.custom_sql, merged_params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result_data = []
                for row in rows:
                    result_data.append(dict(zip(columns, row)))
        else:
            # For standard reports
            # This is a simplified implementation - in a real system,
            # this would use a more sophisticated query builder
            result_data = {"message": "Report generation not fully implemented"}
        
        # Create report data record
        report_data = ReportData.objects.create(
            report=self,
            generated_by=self.created_by,  # Assuming current user is the creator
            format=output_format,
            parameters=merged_params,
            data=result_data
        )
        
        return report_data
    
    def schedule(self, frequency, start_date, recipients=None, format=None):
        """
        Schedule this report to run on a recurring basis.
        
        Args:
            frequency: How often to run the report
            start_date: When to start running the report
            recipients: List of user IDs to receive the report
            format: Output format for the scheduled report
            
        Returns:
            ReportSchedule object
        """
        schedule = ReportSchedule.objects.create(
            report=self,
            frequency=frequency,
            start_date=start_date,
            format=format or self.default_format,
            recipients=recipients or [],
            created_by=self.created_by  # Assuming current user is the creator
        )
        
        return schedule


class ReportTemplate(TimeStampedModel, SoftDeleteModel):
    """
    Model to manage report templates.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    template_type = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.HTML
    )
    content = models.TextField(
        help_text=_("Template content with placeholders")
    )
    css_style = models.TextField(
        blank=True,
        null=True,
        help_text=_("CSS styling for HTML templates")
    )
    header_content = models.TextField(
        blank=True,
        null=True,
        help_text=_("Content for report header")
    )
    footer_content = models.TextField(
        blank=True,
        null=True,
        help_text=_("Content for report footer")
    )
    page_size = models.CharField(
        max_length=20,
        default='A4',
        help_text=_("Page size for PDF templates")
    )
    orientation = models.CharField(
        max_length=20,
        choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')],
        default='portrait',
        help_text=_("Page orientation for PDF templates")
    )
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of variables/placeholders used in the template")
    )
    is_system = models.BooleanField(
        default=False,
        help_text=_("Whether this is a system-defined template")
    )
    thumbnail = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Path to template thumbnail image")
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def render(self, context_data):
        """
        Render the template with the provided context data.
        
        Args:
            context_data: Dictionary of values to replace placeholders
            
        Returns:
            Rendered template content
        """
        from django.template import Template, Context
        
        # Simple template rendering for HTML templates
        if self.template_type == ReportFormat.HTML:
            template = Template(self.content)
            context = Context(context_data)
            return template.render(context)
        
        # For other formats, this would use appropriate libraries
        # like openpyxl for Excel, reportlab for PDF, etc.
        return self.content


class ReportSchedule(TimeStampedModel):
    """
    Model to schedule recurring reports.
    """
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    frequency = models.CharField(
        max_length=20,
        choices=ReportFrequency.choices,
        default=ReportFrequency.MONTHLY
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Optional end date for the schedule")
    )
    time_of_day = models.TimeField(
        default=timezone.now().replace(hour=6, minute=0, second=0, microsecond=0).time(),
        help_text=_("Time of day to generate the report")
    )
    day_of_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text=_("Day of week for weekly reports (0=Monday, 6=Sunday)")
    )
    day_of_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text=_("Day of month for monthly reports")
    )
    month_of_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text=_("Month of year for yearly reports")
    )
    format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Parameters to use when generating the report")
    )
    recipients = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of user IDs to receive the report")
    )
    recipient_groups = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of group IDs to receive the report")
    )
    email_subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Subject line for email delivery")
    )
    email_body = models.TextField(
        blank=True,
        null=True,
        help_text=_("Body text for email delivery")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this schedule is active")
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the report was last generated")
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the report is next scheduled to run")
    )
    
    class Meta:
        ordering = ['-is_active', 'next_run']
        indexes = [
            models.Index(fields=['report', 'is_active']),
            models.Index(fields=['next_run']),
        ]
    
    def __str__(self):
        if self.name:
            return self.name
        return f"{self.report.name} - {self.get_frequency_display()}"
    
    def save(self, *args, **kwargs):
        # Calculate next run date if not set
        if self.is_active and not self.next_run:
            self.calculate_next_run()
            
        super().save(*args, **kwargs)
    
    def calculate_next_run(self):
        """Calculate the next run date based on frequency and last run."""
        from datetime import datetime, timedelta
        import calendar
        
        now = timezone.now()
        
        if not self.last_run:
            # First run - use start_date and time_of_day
            base_date = datetime.combine(
                self.start_date,
                self.time_of_day
            )
            base_date = timezone.make_aware(base_date)
            
            # If start date is in the past, calculate next occurrence
            if base_date < now:
                if self.frequency == ReportFrequency.DAILY:
                    base_date = datetime.combine(
                        now.date(),
                        self.time_of_day
                    )
                    base_date = timezone.make_aware(base_date)
                    if base_date < now:
                        base_date += timedelta(days=1)
                else:
                    # For other frequencies, calculate from start_date
                    self.last_run = base_date
                    return self.calculate_next_run()
        else:
            # Subsequent runs - calculate from last_run
            if self.frequency == ReportFrequency.DAILY:
                next_date = self.last_run + timedelta(days=1)
                base_date = datetime.combine(
                    next_date.date(),
                    self.time_of_day
                )
                base_date = timezone.make_aware(base_date)
                
            elif self.frequency == ReportFrequency.WEEKLY:
                days_ahead = self.day_of_week - self.last_run.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                    
                next_date = self.last_run + timedelta(days=days_ahead)
                base_date = datetime.combine(
                    next_date.date(),
                    self.time_of_day
                )
                base_date = timezone.make_aware(base_date)
                
            elif self.frequency == ReportFrequency.MONTHLY:
                next_month = self.last_run.month + 1
                next_year = self.last_run.year
                
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                    
                # Handle edge cases like February 30th
                last_day = calendar.monthrange(next_year, next_month)[1]
                day = min(self.day_of_month or self.last_run.day, last_day)
                
                base_date = datetime(
                    year=next_year,
                    month=next_month,
                    day=day,
                    hour=self.time_of_day.hour,
                    minute=self.time_of_day.minute
                )
                base_date = timezone.make_aware(base_date)
                
            elif self.frequency == ReportFrequency.QUARTERLY:
                # Add 3 months
                next_month = self.last_run.month + 3
                next_year = self.last_run.year
                
                if next_month > 12:
                    next_month = next_month - 12
                    next_year += 1
                    
                # Handle edge cases like February 30th
                last_day = calendar.monthrange(next_year, next_month)[1]
                day = min(self.day_of_month or self.last_run.day, last_day)
                
                base_date = datetime(
                    year=next_year,
                    month=next_month,
                    day=day,
                    hour=self.time_of_day.hour,
                    minute=self.time_of_day.minute
                )
                base_date = timezone.make_aware(base_date)
                
            elif self.frequency == ReportFrequency.YEARLY:
                next_year = self.last_run.year + 1
                month = self.month_of_year or self.last_run.month
                
                # Handle edge cases like February 29th
                last_day = calendar.monthrange(next_year, month)[1]
                day = min(self.day_of_month or self.last_run.day, last_day)
                
                base_date = datetime(
                    year=next_year,
                    month=month,
                    day=day,
                    hour=self.time_of_day.hour,
                    minute=self.time_of_day.minute
                )
                base_date = timezone.make_aware(base_date)
                
            else:  # ONCE
                # One-time reports don't have next runs
                self.next_run = None
                self.is_active = False
                return
        
        # Check if we've passed the end date
        if self.end_date and base_date.date() > self.end_date:
            self.next_run = None
            self.is_active = False
            return
        
        self.next_run = base_date
    
    def run(self):
        """
        Execute the report schedule and generate the report.
        
        Returns:
            ReportData object containing the generated report
        """
        if not self.is_active:
            return None
        
        # Generate the report
        report_data = self.report.generate(
            parameters=self.parameters,
            format=self.format
        )
        
        # Update schedule metadata
        self.last_run = timezone.now()
        self.calculate_next_run()
        self.save()
        
        # Send notifications to recipients
        self.send_notifications(report_data)
        
        return report_data
    
    def send_notifications(self, report_data):
        """
        Send notifications to recipients about the generated report.
        
        Args:
            report_data: ReportData object containing the generated report
        """
        # This would be implemented with Django's email functionality
        # or other notification mechanisms
        pass


class ReportData(TimeStampedModel):
    """
    Model to store generated report data.
    """
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    schedule = models.ForeignKey(
        ReportSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        help_text=_("Schedule that generated this report, if any")
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF
    )
    file_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Path to the generated report file")
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Size of the generated file in bytes")
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Raw data used to generate the report")
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Parameters used to generate the report")
    )
    execution_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Time taken to generate the report in milliseconds")
    )
    row_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Number of data rows in the report")
    )
    is_cached = models.BooleanField(
        default=False,
        help_text=_("Whether this report data is cached")
    )
    cache_expiry = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the cached data expires")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', 'created_at']),
            models.Index(fields=['generated_by', 'created_at']),
        ]
        verbose_name_plural = "Report data"
    
    def __str__(self):
        return f"{self.report.name} - {self.created_at}"
    
    def get_file_url(self):
        """Get the URL to download the report file."""
        if self.file_path:
            from django.urls import reverse
            return reverse('reports:download', args=[self.id])
        return None
    
    def is_expired(self):
        """Check if cached data is expired."""
        if not self.is_cached or not self.cache_expiry:
            return True
        return timezone.now() > self.cache_expiry
