from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.gis.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)
    

# User Model:
# Represents individual users of the platform, which can be farmers or admins.
# Users can own multiple fields and initiate multiple seasons. 
# Each user is associated with standard authentication and permission attributes.
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('admin', 'Admin'),
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="customuser",
        verbose_name=('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="customuser",
        verbose_name=('user permissions')
    )


# Season Model:
# Represents a distinct crop season.
# Owned by a specific user, a season spans a defined period (start and end date).
# During a season, multiple fields can be tracked, and progress over time can be monitored.
class Season(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)


# Field Model:
# Represents a specific agricultural field.
# Each field is owned by a user and can be part of multiple seasons.
# The location attribute consists of lat-lon tuples array.
# The FieldSeasonAssociation model captures the many-to-many relationship between fields and seasons.
class Field(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    location = models.PolygonField()
    description = models.TextField(blank=True, null=True)
    seasons = models.ManyToManyField(Season, through='FieldSeasonAssociation', null=True)
    
# FieldSeasonAssociation Model:
# Serves as an intermediary model to bridge the many-to-many relationship between fields and seasons.
# Represents the association of a field with a particular season.
# Enables tracking of a field's progress and activities during a specific season.
class FieldSeasonAssociation(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    date_associated = models.DateTimeField(default=timezone.now)
    uav_flights = models.ManyToManyField('UAVFlight', through='UAVFlightFieldSeasonAssociation', blank=True)


# UAVFlight Model:
# Represents a UAV flight.
# Each flight can have multiple images associated with it, captured during the flight.
# The model stores information about the flight such as date, time, and any relevant description.
class UAVFlight(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    flight_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    
# FieldImage Model:
# Represents images of a field.
# Each image is tied to a specific field during a particular season via the FieldSeasonAssociation model.
# This structure allows tracking and comparison of field conditions across different seasons.
class FieldImage(models.Model):
    #TODO remove null=True when ready to migrate before production
    uav_flight = models.ForeignKey(UAVFlight, related_name='images', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='field_images/')
    resized_image = models.ImageField(upload_to='resized_field_images/', blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    gps_latitude = models.CharField(max_length=100, blank=True, null=True)
    gps_longitude = models.CharField(max_length=100, blank=True, null=True)
    gps_altitude = models.CharField(max_length=100, blank=True, null=True)

# UAVFlightFieldSeasonAssociation
# This model associates UAV flights with a specific field during a particular season.
# It allows for the independent existence of UAV flights and their later association with fields and seasons.
class UAVFlightFieldSeasonAssociation(models.Model):
    uav_flight = models.ForeignKey('UAVFlight', on_delete=models.CASCADE)
    field_season = models.ForeignKey('FieldSeasonAssociation', on_delete=models.CASCADE)


# ProcessingResult Model:
# Represents the outcome of processing a field image (e.g., detecting weeds using deep learning).
# Each processing result is directly linked to a FieldImage.
# Provides insights and analyses based on the images uploaded for a field in a particular season.
class ProcessingResult(models.Model):
    image = models.ForeignKey(FieldImage, on_delete=models.CASCADE, null=True)
    result_data = models.JSONField(default=dict, blank=True, null=True)
    date_processed = models.DateTimeField(default=timezone.now)
    generated_image = models.ImageField(upload_to='generated_images/', blank=True, null=True)  # For storing the analyzed image


class AnalysisJob(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )
    #TODO remove null=True when ready to migrate before production
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    uav_flight = models.ForeignKey(UAVFlight, on_delete=models.CASCADE, null=True)
    field_image = models.ForeignKey(FieldImage, on_delete=models.CASCADE, null=True, blank=True)