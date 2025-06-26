from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, SoftDeleteModel, Address
from employees.models import Employee


class AccommodationType(models.TextChoices):
    APARTMENT = 'apartment', _('Apartment')
    HOUSE = 'house', _('House')
    DORMITORY = 'dormitory', _('Dormitory')
    SHARED_ROOM = 'shared_room', _('Shared Room')
    SINGLE_ROOM = 'single_room', _('Single Room')
    VILLA = 'villa', _('Villa')
    OTHER = 'other', _('Other')


class AccommodationStatus(models.TextChoices):
    AVAILABLE = 'available', _('Available')
    OCCUPIED = 'occupied', _('Occupied')
    UNDER_MAINTENANCE = 'under_maintenance', _('Under Maintenance')
    RESERVED = 'reserved', _('Reserved')
    DECOMMISSIONED = 'decommissioned', _('Decommissioned')


class MaintenanceRequestStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')
    REJECTED = 'rejected', _('Rejected')


class MaintenanceRequestPriority(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')
    EMERGENCY = 'emergency', _('Emergency')


class MaintenanceRequestType(models.TextChoices):
    PLUMBING = 'plumbing', _('Plumbing')
    ELECTRICAL = 'electrical', _('Electrical')
    HVAC = 'hvac', _('HVAC')
    STRUCTURAL = 'structural', _('Structural')
    APPLIANCE = 'appliance', _('Appliance')
    FURNITURE = 'furniture', _('Furniture')
    PEST_CONTROL = 'pest_control', _('Pest Control')
    CLEANING = 'cleaning', _('Cleaning')
    OTHER = 'other', _('Other')


class UtilityType(models.TextChoices):
    ELECTRICITY = 'electricity', _('Electricity')
    WATER = 'water', _('Water')
    GAS = 'gas', _('Gas')
    INTERNET = 'internet', _('Internet')
    CABLE = 'cable', _('Cable TV')
    OTHER = 'other', _('Other')


class Accommodation(TimeStampedModel, SoftDeleteModel):
    """
    Model to store details of company accommodations.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    accommodation_type = models.CharField(
        max_length=20,
        choices=AccommodationType.choices,
        default=AccommodationType.APARTMENT
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accommodations'
    )
    status = models.CharField(
        max_length=20,
        choices=AccommodationStatus.choices,
        default=AccommodationStatus.AVAILABLE
    )
    capacity = models.PositiveIntegerField(
        default=1,
        help_text=_("Number of people this accommodation can house")
    )
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area_sqft = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Area in square feet")
    )
    floor = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Floor number or description")
    )
    building = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Building name or number")
    )
    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Monthly rent amount")
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Security deposit amount")
    )
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)
    landlord_name = models.CharField(max_length=100, blank=True, null=True)
    landlord_contact = models.CharField(max_length=100, blank=True, null=True)
    is_company_owned = models.BooleanField(
        default=True,
        help_text=_("Whether this accommodation is owned by the company or leased")
    )
    amenities = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of amenities available")
    )
    furnishing_status = models.CharField(
        max_length=20,
        choices=[
            ('unfurnished', 'Unfurnished'),
            ('semi_furnished', 'Semi-Furnished'),
            ('fully_furnished', 'Fully Furnished'),
        ],
        default='fully_furnished'
    )
    notes = models.TextField(blank=True, null=True)
    images = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of image URLs")
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['accommodation_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_available(self):
        """Check if the accommodation is available for allocation."""
        return self.status == AccommodationStatus.AVAILABLE
    
    @property
    def current_allocation(self):
        """Get the current allocation for this accommodation."""
        return self.allocations.filter(
            is_active=True,
            end_date__isnull=True
        ).first()
    
    @property
    def current_occupants(self):
        """Get the current occupants of this accommodation."""
        allocation = self.current_allocation
        if allocation:
            return allocation.occupants.all()
        return Employee.objects.none()
    
    @property
    def occupancy_rate(self):
        """Calculate the occupancy rate as a percentage."""
        if self.capacity == 0:
            return 0
        
        current_occupants = self.current_occupants.count()
        return (current_occupants / self.capacity) * 100
    
    def mark_occupied(self):
        """Mark the accommodation as occupied."""
        self.status = AccommodationStatus.OCCUPIED
        self.save()
    
    def mark_available(self):
        """Mark the accommodation as available."""
        self.status = AccommodationStatus.AVAILABLE
        self.save()
    
    def mark_under_maintenance(self):
        """Mark the accommodation as under maintenance."""
        self.status = AccommodationStatus.UNDER_MAINTENANCE
        self.save()


class AccommodationAllocation(TimeStampedModel, SoftDeleteModel):
    """
    Model to track which employee is assigned to which accommodation.
    """
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    primary_occupant = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='primary_accommodations'
    )
    occupants = models.ManyToManyField(
        Employee,
        related_name='accommodations',
        help_text=_("All occupants including the primary occupant")
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this allocation is currently active")
    )
    rent_deduction = models.BooleanField(
        default=True,
        help_text=_("Whether rent should be deducted from salary")
    )
    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Monthly rent amount to be deducted")
    )
    allocation_type = models.CharField(
        max_length=20,
        choices=[
            ('permanent', 'Permanent'),
            ('temporary', 'Temporary'),
        ],
        default='permanent'
    )
    allocated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='allocations_made'
    )
    check_in_notes = models.TextField(blank=True, null=True)
    check_out_notes = models.TextField(blank=True, null=True)
    check_in_inventory = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Inventory at check-in")
    )
    check_out_inventory = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Inventory at check-out")
    )
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['accommodation', 'is_active']),
            models.Index(fields=['primary_occupant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.accommodation.name} - {self.primary_occupant.full_name} ({self.start_date})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # If this is a new active allocation, update accommodation status
        if is_new and self.is_active:
            self.accommodation.mark_occupied()
            
            # Add primary occupant to occupants if not already added
            self.occupants.add(self.primary_occupant)
    
    def end_allocation(self, end_date=None, check_out_notes=None, check_out_inventory=None):
        """End the accommodation allocation."""
        self.end_date = end_date or timezone.now().date()
        self.is_active = False
        
        if check_out_notes:
            self.check_out_notes = check_out_notes
            
        if check_out_inventory:
            self.check_out_inventory = check_out_inventory
            
        self.save()
        
        # Check if there are other active allocations for this accommodation
        other_active = AccommodationAllocation.objects.filter(
            accommodation=self.accommodation,
            is_active=True
        ).exclude(pk=self.pk).exists()
        
        # If no other active allocations, mark accommodation as available
        if not other_active:
            self.accommodation.mark_available()
    
    @property
    def duration(self):
        """Calculate the duration of the allocation in days."""
        if not self.end_date:
            return (timezone.now().date() - self.start_date).days
        return (self.end_date - self.start_date).days
    
    @property
    def occupant_count(self):
        """Get the number of occupants."""
        return self.occupants.count()


class MaintenanceRequest(TimeStampedModel):
    """
    Model to manage maintenance requests for accommodations.
    """
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    request_type = models.CharField(
        max_length=20,
        choices=MaintenanceRequestType.choices,
        default=MaintenanceRequestType.OTHER
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=MaintenanceRequestPriority.choices,
        default=MaintenanceRequestPriority.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceRequestStatus.choices,
        default=MaintenanceRequestStatus.PENDING
    )
    requested_date = models.DateField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance_requests'
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Estimated cost of repair")
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Actual cost of repair")
    )
    vendor_name = models.CharField(max_length=100, blank=True, null=True)
    vendor_contact = models.CharField(max_length=100, blank=True, null=True)
    images_before = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of image URLs before repair")
    )
    images_after = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of image URLs after repair")
    )
    resolution_notes = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rating from 1-5")
    )
    
    class Meta:
        ordering = ['-requested_date', 'priority']
        indexes = [
            models.Index(fields=['accommodation', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.accommodation.name} - {self.title} ({self.get_status_display()})"
    
    def assign(self, employee, scheduled_date=None):
        """Assign the maintenance request to an employee."""
        self.assigned_to = employee
        if scheduled_date:
            self.scheduled_date = scheduled_date
        self.status = MaintenanceRequestStatus.IN_PROGRESS
        self.save()
    
    def complete(self, resolution_notes=None, actual_cost=None, images_after=None):
        """Mark the maintenance request as completed."""
        self.status = MaintenanceRequestStatus.COMPLETED
        self.completed_date = timezone.now().date()
        
        if resolution_notes:
            self.resolution_notes = resolution_notes
            
        if actual_cost is not None:
            self.actual_cost = actual_cost
            
        if images_after:
            self.images_after = images_after
            
        self.save()
        
        # If accommodation was under maintenance, check if there are other pending requests
        if self.accommodation.status == AccommodationStatus.UNDER_MAINTENANCE:
            pending_requests = MaintenanceRequest.objects.filter(
                accommodation=self.accommodation,
                status__in=[
                    MaintenanceRequestStatus.PENDING,
                    MaintenanceRequestStatus.IN_PROGRESS
                ]
            ).exclude(pk=self.pk).exists()
            
            # If no other pending requests, mark accommodation as available or occupied
            if not pending_requests:
                if self.accommodation.current_allocation:
                    self.accommodation.mark_occupied()
                else:
                    self.accommodation.mark_available()
    
    def cancel(self):
        """Cancel the maintenance request."""
        self.status = MaintenanceRequestStatus.CANCELLED
        self.save()
    
    def reject(self, reason):
        """Reject the maintenance request."""
        self.status = MaintenanceRequestStatus.REJECTED
        self.resolution_notes = reason
        self.save()
    
    def provide_feedback(self, feedback, rating):
        """Provide feedback and rating for completed maintenance."""
        if self.status != MaintenanceRequestStatus.COMPLETED:
            raise ValueError("Feedback can only be provided for completed requests")
            
        self.feedback = feedback
        self.rating = rating
        self.save()
    
    @property
    def is_overdue(self):
        """Check if the maintenance request is overdue."""
        if self.status not in [MaintenanceRequestStatus.PENDING, MaintenanceRequestStatus.IN_PROGRESS]:
            return False
            
        if self.scheduled_date and self.scheduled_date < timezone.now().date():
            return True
            
        return False
    
    @property
    def days_pending(self):
        """Calculate the number of days the request has been pending."""
        if self.status == MaintenanceRequestStatus.PENDING:
            return (timezone.now().date() - self.requested_date).days
        return 0


class UtilityReading(TimeStampedModel):
    """
    Model to track utility meter readings.
    """
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name='utility_readings'
    )
    utility_type = models.CharField(
        max_length=20,
        choices=UtilityType.choices,
        default=UtilityType.ELECTRICITY
    )
    reading_date = models.DateField()
    reading_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Meter reading value")
    )
    unit = models.CharField(
        max_length=20,
        default='kWh',
        help_text=_("Unit of measurement (kWh, cubic meters, etc.)")
    )
    is_initial_reading = models.BooleanField(
        default=False,
        help_text=_("Whether this is the initial reading for a new allocation")
    )
    is_final_reading = models.BooleanField(
        default=False,
        help_text=_("Whether this is the final reading for an ended allocation")
    )
    allocation = models.ForeignKey(
        AccommodationAllocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utility_readings',
        help_text=_("Associated allocation if applicable")
    )
    bill_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Bill amount based on this reading")
    )
    bill_paid = models.BooleanField(
        default=False,
        help_text=_("Whether the bill has been paid")
    )
    bill_paid_date = models.DateField(null=True, blank=True)
    bill_paid_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_utility_bills'
    )
    notes = models.TextField(blank=True, null=True)
    image = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Image of the meter reading")
    )
    
    class Meta:
        ordering = ['-reading_date', 'accommodation']
        indexes = [
            models.Index(fields=['accommodation', 'utility_type', 'reading_date']),
            models.Index(fields=['allocation']),
        ]
    
    def __str__(self):
        return f"{self.accommodation.name} - {self.get_utility_type_display()} - {self.reading_date}"
    
    @property
    def previous_reading(self):
        """Get the previous reading for this utility type and accommodation."""
        return UtilityReading.objects.filter(
            accommodation=self.accommodation,
            utility_type=self.utility_type,
            reading_date__lt=self.reading_date
        ).order_by('-reading_date').first()
    
    @property
    def consumption(self):
        """Calculate consumption since the previous reading."""
        previous = self.previous_reading
        if previous:
            return self.reading_value - previous.reading_value
        return 0
    
    def mark_paid(self, paid_by=None, paid_date=None):
        """Mark the utility bill as paid."""
        self.bill_paid = True
        self.bill_paid_date = paid_date or timezone.now().date()
        self.bill_paid_by = paid_by
        self.save()
