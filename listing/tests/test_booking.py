import pytest
from django.urls import reverse
from rest_framework import status
from listing.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_tenant_can_view_own_booking(api_client, tenant_user, booking):
    api_client.force_authenticate(user=tenant_user)
    url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_tenant_cannot_view_others_booking(api_client, booking):
    another_tenant = User.objects.create_user(username='tenant2', email='tenant@example.com', password='password123', role='tenant')
    api_client.force_authenticate(user=another_tenant)
    url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
    response = api_client.get(url)
    print(response.status_code, response.data)  # Отладочный вывод для проверки
    assert response.status_code in {status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND}

@pytest.mark.django_db
def test_landlord_can_view_booking_for_own_property(api_client, landlord_user, booking):
    api_client.force_authenticate(user=landlord_user)
    url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
