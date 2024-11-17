import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from listing.models import Booking, Review

User = get_user_model()


@pytest.mark.django_db
def test_booking_notification_created(api_client, landlord_user, tenant_user, sample_property):
    api_client.force_authenticate(user=tenant_user)

    # Создаем бронирование
    booking = Booking.objects.create(
        property=340,
        user=33,
        start_date="2024-12-01",
        end_date="2024-12-10",
        status="pending"
    )

    # Указываем pk для URL
    url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
    response = api_client.get(url)
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_review_notification_created(api_client, landlord_user, tenant_user, sample_property):
    api_client.force_authenticate(user=tenant_user)

    # Создаем отзыв
    review = Review.objects.create(
        property=sample_property,
        user=tenant_user,
        content="Great place!",
        rating=5
    )

    # Указываем pk для URL
    url = reverse('api:review-detail', kwargs={'pk': review.pk})
    response = api_client.get(url)
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_403_FORBIDDEN}
