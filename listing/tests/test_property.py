import pytest
from django.urls import reverse
from rest_framework import status
from listing.models import Property, Booking, Review, Notification

@pytest.mark.django_db
def test_create_property(api_client, landlord_user):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:properties-list')
    data = {
        "title": "Test Property",
        "description": "A cozy apartment in the city center",
        "location": "Berlin",
        "price": "1500",  # строка, как в JSON-примере
        "room_count": 2,
        "property_type": "apartment",
        "status": "active",
        "created_at": "2024-11-14T01:38:57.891495Z",
        "views": 0,
        "owner": 30,  # ID пользователя landlord
        "categories": [7]  # Убедитесь, что категория с ID 1 существует
    }
    response = api_client.post(url, data)
    print(response.data)  # Для отладки
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == data['title']

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
        'title': 'Updated Property',
        'created_at': sample_property.created_at  # Добавлено поле created_at
    }
    response = api_client.patch(url, data)
    print(response.data)  # Для отладки
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == data['title']

@pytest.mark.django_db
def test_delete_property(api_client, landlord_user, sample_property):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:properties-detail', kwargs={'pk': sample_property.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
