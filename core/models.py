from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid
import json


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="%(class)s_created",
        help_text=_("User who created this record")
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="%(class)s_updated",
        help_text=_("User who last updated this record")
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    An abstract base class model that provides a is_deleted field and methods
    to soft delete and restore objects.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="%(class)s_deleted"
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()


class Address(TimeStampedModel):
    """
    A reusable model for storing address information.
    """
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
        help_text=_("Latitude coordinate for mapping")
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
        help_text=_("Longitude coordinate for mapping")
    )
    
    class Meta:
        verbose_name_plural = "Addresses"
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"


class Company(TimeStampedModel, SoftDeleteModel):
    """
    Model to store company information.
    """
    name = models.CharField(max_length=255, help_text=_("Company name"))
    legal_name = models.CharField(max_length=255, help_text=_("Legal registered name of the company"))
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True, help_text=_("Tax identification number"))
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    established_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name


class Department(TimeStampedModel, SoftDeleteModel):
    """
    Model to represent departments within the company.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text=_("Department code"))
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sub_departments',
        help_text=_("Parent department if this is a sub-department")
    )
    head = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='headed_departments',
        help_text=_("Department head/manager")
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Store(TimeStampedModel, SoftDeleteModel):
    """
    Model to represent individual stores/branches of the company.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, help_text=_("Store/branch code"))
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stores')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_stores',
        help_text=_("Store manager")
    )
    opening_date = models.DateField(blank=True, null=True)
    closing_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    geofence_radius = models.IntegerField(
        default=100, 
        help_text=_("Radius in meters for geofencing around the store location")
    )
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_open(self):
        return self.is_active and (self.closing_date is None or self.closing_date > timezone.now().date())


class Role(TimeStampedModel):
    """
    Model to define roles within the organization.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    permissions = models.TextField(
        blank=True, 
        null=True,
        help_text=_("JSON string of permission mappings")
    )
    
    def __str__(self):
        return self.name
    
    def get_permissions(self):
        """Return permissions as a Python dictionary."""
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_permissions(self, permissions_dict):
        """Set permissions from a Python dictionary."""
        self.permissions = json.dumps(permissions_dict)
        self.save()


class AuditLog(models.Model):
    """
    Model to track changes to records across the system.
    """
    ACTIONS = (
        ('C', 'Create'),
        ('U', 'Update'),
        ('D', 'Delete'),
        ('R', 'Restore'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_type = models.CharField(max_length=255, help_text=_("Model being audited"))
    object_id = models.CharField(max_length=50, help_text=_("Primary key of the object"))
    action = models.CharField(max_length=1, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    changes = models.JSONField(default=dict, help_text=_("JSON representation of changes"))
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} on {self.content_type} {self.object_id} by {self.user}"


class SystemConfig(TimeStampedModel):
    """
    Model to store system-wide configuration settings.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('date', 'Date'),
            ('datetime', 'DateTime'),
        ],
        default='string'
    )
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(
        default=False, 
        help_text=_("Whether this setting can be viewed by non-admin users")
    )
    
    def __str__(self):
        return self.key
    
    def get_typed_value(self):
        """Return the value converted to its proper Python type."""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', 'yes', '1')
        elif self.value_type == 'json':
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return None
        elif self.value_type == 'date':
            try:
                return timezone.datetime.strptime(self.value, '%Y-%m-%d').date()
            except ValueError:
                return None
        elif self.value_type == 'datetime':
            try:
                return timezone.datetime.strptime(self.value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
        else:  # string or any other type
            return self.value


class Notification(TimeStampedModel):
    """
    Model to store notifications for users.
    """
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True, help_text=_("Optional link to redirect when clicked"))
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True, null=True, help_text=_("Category for grouping notifications"))
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class Document(TimeStampedModel, SoftDeleteModel):
    """
    Model to store documents and files.
    """
    DOCUMENT_TYPES = (
        ('policy', 'Policy Document'),
        ('contract', 'Contract'),
        ('id_proof', 'ID Proof'),
        ('certificate', 'Certificate'),
        ('resume', 'Resume/CV'),
        ('letter', 'Letter'),
        ('report', 'Report'),
        ('invoice', 'Invoice'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    reference_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=_("Reference ID of related entity")
    )
    reference_type = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=_("Type of entity this document is related to")
    )
    expiry_date = models.DateField(blank=True, null=True)
    is_confidential = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, null=True, help_text=_("Comma-separated tags"))
    
    def __str__(self):
        return self.title
    
    @property
    def file_extension(self):
        name = self.file.name
        return name.split('.')[-1] if '.' in name else ''
    
    @property
    def file_size_kb(self):
        try:
            return round(self.file.size / 1024, 2)
        except:
            return 0
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class ActivityLog(models.Model):
    """
    Model to log user activities in the system.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    module = models.CharField(max_length=100, blank=True, null=True, help_text=_("System module where activity occurred"))
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Activity Logs"
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.activity} - {self.timestamp}"
