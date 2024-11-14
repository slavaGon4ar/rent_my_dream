import pytest
from django.urls import reverse
from rest_framework import status
from listing.models import Notification
from listing.models import Property, Booking, Review, Notification


@pytest.mark.django_db
def test_booking_notification_created(api_client, landlord_user, tenant_user, sample_property):
    api_client.force_authenticate(user=tenant_user)
    url = reverse('api:bookings')
    data = {'property': sample_property.id, 'start_date': '2024-12-01', 'end_date': '2024-12-10'}
    api_client.post(url, data)
    notification = Notification.objects.filter(recipient=landlord_user, event_type='booking_created')
    assert notification.count() == 1

@pytest.mark.django_db
def test_review_notification_created(api_client, landlord_user, tenant_user, sample_property):
    api_client.force_authenticate(user=tenant_user)
    url = reverse('api:reviews')
    data = {'property': sample_property.id, 'rating': 5, 'comment': 'Great place!'}
    api_client.post(url, data)
    notification = Notification.objects.filter(recipient=landlord_user, event_type='new_review')
    assert notification.count() == 1
