from datetime import datetime
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from listing.models import Property, Booking, Review, Notification, Category

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def tenant_user(db):
    return User.objects.create_user(username='tenant1', email='tenant@example.com', password='password123', role='tenant')

@pytest.fixture
def landlord_user(db):
    user, created = User.objects.get_or_create(
        id=30,  # Указание id для landlord
        username='landlord',
        defaults={
            'email': 'landlord@example.com',
            'password': 'password123',
            'role': 'landlord'
        }
    )
    return user

@pytest.fixture
def category1(db):
    return Category.objects.create(id=9, name="Test Category")

@pytest.fixture
def sample_property(db, landlord_user, category1):
    property_instance = Property.objects.create(
        title='Sample Property',
        description='Description of sample property',
        location='Berlin',
        price='1000.00',
        room_count=2,
        property_type='apartment',
        status='active',
        views=4294967295,
        created_at=datetime.now(),
        owner=landlord_user  # Ссылка на landlord_user
    )
    property_instance.categories.set([category1])  # Применение set() для ManyToMany
    return property_instance

@pytest.fixture
def booking(db, tenant_user, sample_property):
    return Booking.objects.create(
        property=sample_property,
        user=tenant_user,
        start_date='2024-12-01',
        end_date='2024-12-10',
        status='pending'
    )
