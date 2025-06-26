from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, SoftDeleteModel, Department, Store, Role, Address, Document
import uuid


class EmployeeStatus(models.TextChoices):
    ACTIVE = 'active', _('Active')
    PROBATION = 'probation', _('Probation')
    NOTICE_PERIOD = 'notice_period', _('Notice Period')
    TERMINATED = 'terminated', _('Terminated')
    RETIRED = 'retired', _('Retired')
    SABBATICAL = 'sabbatical', _('Sabbatical')
    SUSPENDED = 'suspended', _('Suspended')
    ON_LEAVE = 'on_leave', _('On Leave')


class MaritalStatus(models.TextChoices):
    SINGLE = 'single', _('Single')
    MARRIED = 'married', _('Married')
    DIVORCED = 'divorced', _('Divorced')
    WIDOWED = 'widowed', _('Widowed')
    SEPARATED = 'separated', _('Separated')
    OTHER = 'other', _('Other')


class BloodGroup(models.TextChoices):
    A_POSITIVE = 'A+', _('A+')
    A_NEGATIVE = 'A-', _('A-')
    B_POSITIVE = 'B+', _('B+')
    B_NEGATIVE = 'B-', _('B-')
    AB_POSITIVE = 'AB+', _('AB+')
    AB_NEGATIVE = 'AB-', _('AB-')
    O_POSITIVE = 'O+', _('O+')
    O_NEGATIVE = 'O-', _('O-')
    UNKNOWN = 'unknown', _('Unknown')


class Employee(TimeStampedModel, SoftDeleteModel):
    """
    Main employee model to store all employee information.
    """
    # Basic Information
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='employee_profile',
        help_text=_("User account associated with this employee")
    )
    employee_id = models.CharField(
        max_length=50, 
        unique=True,
        help_text=_("Unique employee identification number")
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(
        # 17 characters in "prefer_not_to_say"  → set a bit larger for safety
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say')
        ]
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE
    )
    blood_group = models.CharField(
        max_length=10,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN
    )
    nationality = models.CharField(max_length=100, default='Indian')
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    primary_phone = models.CharField(validators=[phone_regex], max_length=17)
    secondary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    personal_email = models.EmailField()
    official_email = models.EmailField(unique=True)
    
    # Address Information
    current_address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='employee_current_addresses'
    )
    permanent_address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='employee_permanent_addresses'
    )
    
    # Employment Information
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='employees'
    )
    store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='employees'
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='employees'
    )
    reporting_manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('intern', 'Intern'),
            ('probation', 'Probation'),
            ('consultant', 'Consultant')
        ],
        default='full_time'
    )
    date_joined = models.DateField()
    probation_end_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    notice_period_days = models.PositiveIntegerField(default=30)
    last_working_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.PROBATION
    )
    
    # Financial Information
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    uan_number = models.CharField(max_length=12, blank=True, null=True, help_text=_("Universal Account Number for PF"))
    esic_number = models.CharField(max_length=20, blank=True, null=True, help_text=_("Employee State Insurance Corporation Number"))
    
    # Additional Information
    skills = models.ManyToManyField('Skill', blank=True, related_name='employees')
    languages = models.ManyToManyField('Language', blank=True, through='EmployeeLanguage')
    is_remote_worker = models.BooleanField(default=False)
    requires_accommodation = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='employee_qrcodes/', blank=True, null=True)
    location_tracking_enabled = models.BooleanField(default=True, help_text=_("Whether location tracking is enabled for this employee"))
    
    class Meta:
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['department', 'store']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def service_duration(self):
        """Return the service duration in years and months."""
        if not self.date_joined:
            return "N/A"
        
        end_date = self.last_working_date if self.last_working_date else timezone.now().date()
        delta = (end_date.year - self.date_joined.year) * 12 + (end_date.month - self.date_joined.month)
        years = delta // 12
        months = delta % 12
        
        if years == 0:
            return f"{months} month{'s' if months != 1 else ''}"
        return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
    
    def is_manager(self):
        """Check if the employee is a manager (has subordinates)."""
        return self.subordinates.filter(is_deleted=False).exists()
    
    def get_documents(self):
        """Get all documents related to this employee."""
        return EmployeeDocument.objects.filter(employee=self, is_deleted=False)


class EmployeeDocument(TimeStampedModel, SoftDeleteModel):
    """
    Model to store employee-specific documents.
    """
    DOCUMENT_TYPES = (
        ('identity', 'Identity Proof'),
        ('address', 'Address Proof'),
        ('educational', 'Educational Certificate'),
        ('experience', 'Experience Certificate'),
        ('offer_letter', 'Offer Letter'),
        ('joining_letter', 'Joining Letter'),
        ('relieving_letter', 'Relieving Letter'),
        ('salary_slip', 'Salary Slip'),
        ('performance_review', 'Performance Review'),
        ('other', 'Other'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_document_type_display()}"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    def verify(self, user):
        """Mark the document as verified."""
        self.is_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()


class EmergencyContact(TimeStampedModel):
    """
    Model to store emergency contact information for employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    primary_phone = models.CharField(validators=[phone_regex], max_length=17)
    secondary_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False, help_text=_("Whether this is the primary emergency contact"))
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.name} ({self.relationship})"


class Education(TimeStampedModel, SoftDeleteModel):
    """
    Model to store educational qualifications of employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Education"
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.degree} from {self.institution}"


class WorkExperience(TimeStampedModel, SoftDeleteModel):
    """
    Model to store previous work experience of employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_experience')
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reference_name = models.CharField(max_length=255, blank=True, null=True)
    reference_contact = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.job_title} at {self.company_name}"
    
    @property
    def duration(self):
        """Return the duration of work experience in years and months."""
        if not self.start_date:
            return "N/A"
        
        end_date = self.end_date if self.end_date else timezone.now().date()
        delta = (end_date.year - self.start_date.year) * 12 + (end_date.month - self.start_date.month)
        years = delta // 12
        months = delta % 12
        
        if years == 0:
            return f"{months} month{'s' if months != 1 else ''}"
        return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"


class Skill(TimeStampedModel):
    """
    Model to store skills that can be associated with employees.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name


class Language(models.Model):
    """
    Model to store languages.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text=_("ISO language code"))
    
    def __str__(self):
        return self.name


class EmployeeLanguage(models.Model):
    """
    Model to store language proficiency of employees.
    """
    PROFICIENCY_LEVELS = (
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('fluent', 'Fluent'),
        ('native', 'Native'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    reading = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    writing = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    speaking = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    
    class Meta:
        unique_together = ['employee', 'language']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.language.name}"


class EmployeeTransfer(TimeStampedModel):
    """
    Model to track employee transfers between departments/stores.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='transfers')
    from_department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='transfers_from',
        blank=True
    )
    to_department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='transfers_to',
        blank=True
    )
    from_store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='transfers_from',
        blank=True
    )
    to_store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='transfers_to',
        blank=True
    )
    effective_date = models.DateField()
    reason = models.TextField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='completed_transfers'
    )
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - Transfer on {self.effective_date}"
    
    def complete(self, user):
        """Mark the transfer as completed."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()


class EmployeePromotion(TimeStampedModel):
    """
    Model to track employee promotions.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='promotions')
    from_role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='promotions_from'
    )
    to_role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='promotions_to'
    )
    effective_date = models.DateField()
    reason = models.TextField()
    salary_change = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text=_("Salary change amount (if applicable)")
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='completed_promotions'
    )
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - Promotion to {self.to_role.name} on {self.effective_date}"
    
    def complete(self, user):
        """Mark the promotion as completed."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()


class PerformanceReview(TimeStampedModel, SoftDeleteModel):
    """
    Model to store employee performance reviews.
    """
    REVIEW_TYPES = (
        ('probation', 'Probation Review'),
        ('quarterly', 'Quarterly Review'),
        ('half_yearly', 'Half Yearly Review'),
        ('annual', 'Annual Review'),
        ('special', 'Special Review'),
    )
    
    RATING_CHOICES = (
        (1, 'Poor'),
        (2, 'Needs Improvement'),
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    reviewer = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='conducted_reviews'
    )
    overall_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    strengths = models.TextField(blank=True, null=True)
    areas_for_improvement = models.TextField(blank=True, null=True)
    goals_for_next_period = models.TextField(blank=True, null=True)
    employee_comments = models.TextField(blank=True, null=True)
    is_acknowledged_by_employee = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-review_period_end']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_review_type_display()} ({self.review_period_end})"
    
    def acknowledge(self):
        """Mark the review as acknowledged by the employee."""
        self.is_acknowledged_by_employee = True
        self.acknowledged_at = timezone.now()
        self.save()


class EmployeeLocation(models.Model):
    """
    Model to track employee locations for GPS tracking.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    accuracy = models.FloatField(
        null=True, 
        blank=True,
        help_text=_("Accuracy of the location in meters")
    )
    battery_level = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Battery level of the device in percentage")
    )
    device_info = models.JSONField(default=dict, blank=True)
    is_check_in = models.BooleanField(
        default=False,
        help_text=_("Whether this location was recorded during check-in")
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.timestamp}"
