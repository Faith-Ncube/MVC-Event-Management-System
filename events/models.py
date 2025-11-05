from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
import uuid

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=300)
    max_attendees = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    registration_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def registered_attendees_count(self):
        return self.attendees.count()
    
    def available_spots(self):
        return self.max_attendees - self.registered_attendees_count()
    
    def is_full(self):
        return self.registered_attendees_count() >= self.max_attendees

class Attendee(models.Model):
    EVENT_CATEGORIES = [
        ('general', 'General Admission'),
        ('vip', 'VIP'),
        ('speaker', 'Speaker'),
        ('sponsor', 'Sponsor'),
    ]
    
    ATTENDANCE_STATUS = [
        ('registered', 'Registered'),
        ('checked_in', 'Checked In'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Event-specific information
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES, default='general')
    
    # Dietary preferences
    dietary_restrictions = models.TextField(blank=True)
    
    # Registration details
    registration_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    confirmation_code = models.CharField(max_length=20, unique=True, blank=True)
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='registered')
    check_in_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['event', 'email']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Check capacity before saving (database-level protection)
        if not self.pk:  # Only for new registrations, not updates
            if self.event.is_full():
                raise ValidationError("Event is full. Cannot register more attendees.")
        
        if not self.confirmation_code:
            self.confirmation_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=False)

    # Explicitly define groups and user_permissions with unique related_names
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='event_app_customuser_set',  # ← unique name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='event_app_customuser_set',  # ← unique name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email