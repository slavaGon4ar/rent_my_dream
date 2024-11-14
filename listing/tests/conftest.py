from datetime import datetime
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from listing.models import Property, Booking, Review, Notification, Category
from listing.models import User

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def tenant_user(db):
    return User.objects.create_user(username='tenant', email='tenant@example.com', password='password123', role='tenant')

@pytest.fixture
def landlord_user(db):
    return User.objects.create_user(username='landlord', email='landlord@example.com', password='password123', role='landlord')


@pytest.fixture
def sample_property(db):
    # Создаем категорию для примера
    category = Category.objects.create(name="Sample Category")

    # Создаем экземпляр Property с нужными полями
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
        owner_id=30  # ID собственника landlord
    )

    # Добавляем категорию в поле categories
    property_instance.categories.add(category)

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

