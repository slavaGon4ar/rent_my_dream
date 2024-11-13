from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, role='landlord', **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (('tenant', 'Tenant'), ('landlord', 'Landlord'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='listing_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='listing_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = UserManager()  # Используйте кастомный менеджер

class Category(models.Model):
    name = models.CharField(max_length=100)

class Property(models.Model):
    PROPERTY_TYPES = (('apartment', 'Apartment'), ('house', 'House'), ('studio', 'Studio'))
    STATUS_CHOICES = (('active', 'Active'), ('inactive', 'Inactive'))

    title = models.CharField(max_length=255, unique_for_date='created_at')
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    room_count = models.PositiveIntegerField()
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    categories = models.ManyToManyField(Category)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')

class Booking(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'))

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_history')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='view_history')
    created_at = models.DateTimeField(auto_now_add=True)
