from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, SoftDeleteModel, Store
from employees.models import Employee


class TrackingStatus(models.TextChoices):
    ACTIVE = 'active', _('Active')
    INACTIVE = 'inactive', _('Inactive')
    PAUSED = 'paused', _('Paused')
    ERROR = 'error', _('Error')


class GeofenceType(models.TextChoices):
    CIRCLE = 'circle', _('Circle')
    POLYGON = 'polygon', _('Polygon')
    RECTANGLE = 'rectangle', _('Rectangle')


class TrackingEventType(models.TextChoices):
    CHECK_IN = 'check_in', _('Check In')
    CHECK_OUT = 'check_out', _('Check Out')
    LOCATION_UPDATE = 'location_update', _('Location Update')
    GEOFENCE_ENTER = 'geofence_enter', _('Geofence Enter')
    GEOFENCE_EXIT = 'geofence_exit', _('Geofence Exit')
    GEOFENCE_DWELL = 'geofence_dwell', _('Geofence Dwell')


class DeviceType(models.TextChoices):
    ANDROID = 'android', _('Android')
    IOS = 'ios', _('iOS')
    WEB = 'web', _('Web Browser')
    OTHER = 'other', _('Other')


class EmployeeTracking(TimeStampedModel):
    """
    Model to track employee location in real-time.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tracking'
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether location tracking is active for this employee")
    )
    status = models.CharField(
        max_length=20,
        choices=TrackingStatus.choices,
        default=TrackingStatus.ACTIVE
    )
    last_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_("Last recorded latitude")
    )
    last_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_("Last recorded longitude")
    )
    last_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of last location update")
    )
    last_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Accuracy of last location in meters")
    )
    last_battery_level = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Battery level at last update (percentage)")
    )
    current_store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='currently_tracked_employees',
        help_text=_("Store where employee is currently located")
    )
    current_geofence = models.ForeignKey(
        'GeofenceArea',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='currently_tracked_employees',
        help_text=_("Geofence where employee is currently located")
    )
    tracking_enabled_since = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When tracking was last enabled")
    )
    device = models.ForeignKey(
        'DeviceInfo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_sessions'
    )
    
    class Meta:
        ordering = ['-last_update']
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['last_update']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_status_display()}"
    
    def update_location(self, latitude, longitude, accuracy=None, battery_level=None):
        """Update the employee's current location."""
        self.last_latitude = latitude
        self.last_longitude = longitude
        self.last_update = timezone.now()
        
        if accuracy is not None:
            self.last_accuracy = accuracy
            
        if battery_level is not None:
            self.last_battery_level = battery_level
        
        # Check if employee is within any geofence
        geofences = GeofenceArea.objects.filter(is_active=True)
        current_geofence = None
        
        for geofence in geofences:
            if geofence.contains_point(latitude, longitude):
                current_geofence = geofence
                break
        
        # Update current geofence
        if current_geofence != self.current_geofence:
            # If entering a new geofence
            if current_geofence:
                TrackingLog.objects.create(
                    employee=self.employee,
                    event_type=TrackingEventType.GEOFENCE_ENTER,
                    latitude=latitude,
                    longitude=longitude,
                    accuracy=accuracy,
                    battery_level=battery_level,
                    geofence=current_geofence
                )
            
            # If leaving a geofence
            if self.current_geofence:
                TrackingLog.objects.create(
                    employee=self.employee,
                    event_type=TrackingEventType.GEOFENCE_EXIT,
                    latitude=latitude,
                    longitude=longitude,
                    accuracy=accuracy,
                    battery_level=battery_level,
                    geofence=self.current_geofence
                )
        
        self.current_geofence = current_geofence
        
        # Check if employee is within any store
        stores = Store.objects.filter(is_active=True)
        current_store = None
        
        for store in stores:
            if store.address and store.address.latitude and store.address.longitude:
                # Check if within store's geofence radius
                if self.is_within_radius(
                    latitude, 
                    longitude, 
                    float(store.address.latitude), 
                    float(store.address.longitude),
                    store.geofence_radius
                ):
                    current_store = store
                    break
        
        self.current_store = current_store
        self.save()
        
        # Create tracking log entry
        TrackingLog.objects.create(
            employee=self.employee,
            event_type=TrackingEventType.LOCATION_UPDATE,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            battery_level=battery_level,
            geofence=current_geofence,
            store=current_store
        )
        
        return self
    
    def enable_tracking(self):
        """Enable tracking for this employee."""
        self.is_active = True
        self.status = TrackingStatus.ACTIVE
        self.tracking_enabled_since = timezone.now()
        self.save()
    
    def disable_tracking(self):
        """Disable tracking for this employee."""
        self.is_active = False
        self.status = TrackingStatus.INACTIVE
        self.save()
    
    def is_within_radius(self, lat1, lon1, lat2, lon2, radius_meters):
        """Check if a point is within a certain radius of another point."""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(float(lat1))
        lon1_rad = math.radians(float(lon1))
        lat2_rad = math.radians(float(lat2))
        lon2_rad = math.radians(float(lon2))
        
        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371000  # Radius of earth in meters
        
        # Calculate distance
        distance = c * r
        
        return distance <= radius_meters
    
    @property
    def is_stale(self):
        """Check if the tracking data is stale (no updates for more than 15 minutes)."""
        if not self.last_update:
            return True
        
        time_diff = timezone.now() - self.last_update
        return time_diff.total_seconds() > 900  # 15 minutes in seconds


class GeofenceArea(TimeStampedModel, SoftDeleteModel):
    """
    Model to define geofence areas for employee tracking.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    geofence_type = models.CharField(
        max_length=20,
        choices=GeofenceType.choices,
        default=GeofenceType.CIRCLE
    )
    center_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_("Center latitude for circle geofence")
    )
    center_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_("Center longitude for circle geofence")
    )
    radius = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Radius in meters for circle geofence")
    )
    coordinates = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Coordinates for polygon or rectangle geofence")
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='geofences'
    )
    is_active = models.BooleanField(default=True)
    color = models.CharField(
        max_length=20,
        default='#3388ff',
        help_text=_("Color for displaying the geofence on map")
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_geofence_type_display()})"
    
    def contains_point(self, latitude, longitude):
        """Check if a point is within this geofence."""
        if not self.is_active:
            return False
        
        if self.geofence_type == GeofenceType.CIRCLE:
            if not (self.center_latitude and self.center_longitude and self.radius):
                return False
            
            import math
            
            # Convert latitude and longitude from degrees to radians
            lat1_rad = math.radians(float(latitude))
            lon1_rad = math.radians(float(longitude))
            lat2_rad = math.radians(float(self.center_latitude))
            lon2_rad = math.radians(float(self.center_longitude))
            
            # Haversine formula
            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371000  # Radius of earth in meters
            
            # Calculate distance
            distance = c * r
            
            return distance <= self.radius
        
        elif self.geofence_type == GeofenceType.POLYGON:
            # Ray casting algorithm for point in polygon
            if not self.coordinates:
                return False
            
            point = (float(latitude), float(longitude))
            polygon = self.coordinates
            
            # Check if point is inside polygon
            inside = False
            n = len(polygon)
            p1x, p1y = polygon[0]
            
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if point[1] > min(p1y, p2y):
                    if point[1] <= max(p1y, p2y):
                        if point[0] <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (point[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or point[0] <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            
            return inside
        
        elif self.geofence_type == GeofenceType.RECTANGLE:
            if not self.coordinates or len(self.coordinates) < 2:
                return False
            
            # Rectangle is defined by two points: top-left and bottom-right
            top_left = self.coordinates[0]
            bottom_right = self.coordinates[1]
            
            # Check if point is inside rectangle
            return (float(latitude) >= top_left[0] and float(latitude) <= bottom_right[0] and
                    float(longitude) >= top_left[1] and float(longitude) <= bottom_right[1])
        
        return False


class TrackingLog(models.Model):
    """
    Model to store historical tracking data.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tracking_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=20,
        choices=TrackingEventType.choices,
        default=TrackingEventType.LOCATION_UPDATE
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Accuracy of location in meters")
    )
    battery_level = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Battery level in percentage")
    )
    geofence = models.ForeignKey(
        GeofenceArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_logs'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_logs'
    )
    device = models.ForeignKey(
        'DeviceInfo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_logs'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    additional_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional tracking data")
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['geofence', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_event_type_display()} - {self.timestamp}"


class DeviceInfo(TimeStampedModel):
    """
    Model to store information about employee devices used for tracking.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    device_id = models.CharField(
        max_length=255,
        help_text=_("Unique identifier for the device")
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.OTHER
    )
    device_model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Model of the device")
    )
    os_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Operating system version")
    )
    app_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Tracking app version")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this device is actively used for tracking")
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the device was last seen")
    )
    fcm_token = models.TextField(
        blank=True,
        null=True,
        help_text=_("Firebase Cloud Messaging token for push notifications")
    )
    device_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Device-specific settings")
    )
    
    class Meta:
        ordering = ['-last_seen']
        unique_together = ['employee', 'device_id']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['employee', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.device_model or self.get_device_type_display()}"
    
    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])
    
    def deactivate(self):
        """Deactivate this device."""
        self.is_active = False
        self.save(update_fields=['is_active'])
