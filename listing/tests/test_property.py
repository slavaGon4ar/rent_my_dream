import pytest
from django.urls import reverse
from rest_framework import status
from listing.models import Property, Booking, Review, Notification
from listing.serializers import PropertySerializer

@pytest.mark.django_db
def test_create_property(api_client, landlord_user, category1):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:properties-list')
    data = {
        "title": "Test Property",
        "description": "A cozy apartment in the city center",
        "location": "Berlin",
        "price": "1000",
        "room_count": 2,
        "property_type": "apartment",
        "status": "active",
        "created_at": "2024-11-14T01:38:57.891495Z",
        "views": 0,
        "owner": landlord_user.id,
        "categories": [category1.id]
    }
    response = api_client.post(url, data)
    print(response.data)  # Для отладки
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_get_property_list(api_client, sample_property):
    url = reverse('api:properties-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_property(api_client, landlord_user, sample_property):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:properties-detail', kwargs={'pk': sample_property.pk})

    data = {
        "title": "Updated Property",
        "description": "Updated description",
        "location": "New Location",
        "price": "1200.00",
        "room_count": 3,
        "property_type": "apartment",
        "status": "active",
        "views": 500,
        "owner": landlord_user.id,
        "categories": [9]
    }

    response = api_client.put(url, data)
    print(response.data)  # Для отладки
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_property(api_client, landlord_user, sample_property):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:properties-detail', kwargs={'pk': sample_property.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_property_serializer_read_only_fields(sample_property):
    data = {
        "title": "Updated Property Title",
        "description": "Updated Description",
        "location": "Updated Location",
        "price": "1500.00",
        "room_count": 3,
        "property_type": "apartment",
        "status": "active",
        "views": 100,
        "owner": sample_property.owner.id,
        "categories": [category.id for category in sample_property.categories.all()]
    }

    serializer = PropertySerializer(instance=sample_property, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    validated_data = serializer.validated_data

    # Проверка, что "created_at" отсутствует в данных
    assert 'created_at' not in validated_data
