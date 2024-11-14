import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from listing.models import Property, Booking, Review, Notification


@pytest.mark.django_db
def test_token_obtain(api_client, tenant_user):
    url = reverse('api:token_obtain_pair')
    response = api_client.post(url, {'username': 'tenant', 'password': 'password123'})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_token_refresh(api_client, tenant_user):
    refresh = RefreshToken.for_user(tenant_user)
    url = reverse('api:token_refresh')
    response = api_client.post(url, {'refresh': str(refresh)})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
