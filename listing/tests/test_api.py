from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from listing.models import User
from listing.models import Property, Booking, Review, SearchHistory, ViewHistory, Notification

User = get_user_model()

class UserAuthenticationTest(APITestCase):
    def setUp(self):
        # Регистрируем пользователя через API
        url = reverse('api:user-list')
        data = {'username': 'tenant1', 'password': 'password123', 'role': 'tenant'}
        self.client.post(url, data)

    def test_token_obtain(self):
        url = reverse('api:token_obtain_pair')
        response = self.client.post(url, {'username': 'tenant1', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        user = User.objects.get(username='tenant1')
        refresh = RefreshToken.for_user(user)
        url = reverse('api:token_refresh')
        response = self.client.post(url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class PropertyCRUDTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        data = {'username': 'landlord', 'password': 'password123', 'role': 'landlord'}
        self.client.post(url, data)
        self.user = User.objects.get(username='landlord')
        self.client.force_authenticate(user=self.user)

    def test_create_property(self):
        url = reverse('api:properties')
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
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    def test_get_property_list(self):
        url = reverse('api:properties')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_property(self):
        property_obj = Property.objects.create(
            title='Объявление для обновления',
            description='Описание',
            location='Munich',
            price=1200,
            room_count=3,
            property_type='house',
            status='active',
            owner=self.user
        )
        url = reverse('api:properties', kwargs={'pk': property_obj.pk})
        updated_data = {'title': 'Обновленное объявление'}
        response = self.client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])

    def test_delete_property(self):
        property_obj = Property.objects.create(
            title='Объявление для удаления',
            description='Описание',
            location='Hamburg',
            price=2000,
            room_count=4,
            property_type='studio',
            status='active',
            owner=self.user
        )
        url = reverse('api:properties', kwargs={'pk': property_obj.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookingAccessTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        tenant_data = {'username': 'tenantuser', 'password': 'password123', 'role': 'tenant'}
        landlord_data = {'username': 'landlorduser', 'password': 'password123', 'role': 'landlord'}
        self.client.post(url, tenant_data)
        self.client.post(url, landlord_data)

        self.tenant = User.objects.get(username='tenantuser')
        self.landlord = User.objects.get(username='landlorduser')

        self.property = Property.objects.create(
            title='Объект для бронирования',
            description='Описание объекта',
            location='Berlin',
            price=1500,
            room_count=2,
            property_type='apartment',
            owner=self.landlord
        )

        self.booking = Booking.objects.create(
            property=self.property,
            user=self.tenant,
            start_date='2024-12-01',
            end_date='2024-12-10',
            status='pending'
        )

    def test_tenant_can_view_own_booking(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('api:booking-detail', kwargs={'pk': self.booking.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tenant_cannot_view_others_booking(self):
        another_tenant = User.objects.create_user(username='another_tenant', password='password123', role='tenant')
        self.client.force_authenticate(user=another_tenant)
        url = reverse('api:booking-detail', kwargs={'pk': self.booking.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_landlord_can_view_booking_for_own_property(self):
        self.client.force_authenticate(user=self.landlord)
        url = reverse('api:booking-detail', kwargs={'pk': self.booking.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PropertyFilterSearchTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        data = {'username': 'landlord', 'password': 'password123', 'role': 'landlord'}
        self.client.post(url, data)
        self.user = User.objects.get(username='landlord')

        Property.objects.create(
            title='Квартира в центре',
            description='Прекрасная квартира в центре Берлина',
            location='Berlin',
            price=1000,
            room_count=2,
            property_type='apartment',
            owner=self.user
        )
        Property.objects.create(
            title='Уютный дом в Мюнхене',
            description='Большой дом с садом',
            location='Munich',
            price=2000,
            room_count=4,
            property_type='house',
            owner=self.user
        )

    def test_search_by_keyword(self):
        url = reverse('api:properties')
        response = self.client.get(url, {'search': 'квартира'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Квартира в центре')

    def test_filter_by_price_range(self):
        url = reverse('api:properties')
        response = self.client.get(url, {'price__gte': 1500, 'price__lte': 2500})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Уютный дом в Мюнхене')

    def test_combined_filtering(self):
        url = reverse('api:properties')
        response = self.client.get(url, {'location': 'Berlin', 'price__lte': 1500})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Квартира в центре')


class SearchHistoryTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        data = {'username': 'user1', 'password': 'password123'}
        self.client.post(url, data)
        self.user = User.objects.get(username='user1')
        self.client.force_authenticate(user=self.user)

    def test_search_history_recorded(self):
        url = reverse('api:properties')
        response = self.client.get(url, {'search': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        history = SearchHistory.objects.filter(user=self.user, keyword='Berlin')
        self.assertEqual(history.count(), 1)


class ViewHistoryTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        data = {'username': 'user1', 'password': 'password123'}
        self.client.post(url, data)
        self.user = User.objects.get(username='user1')
        self.property = Property.objects.create(
            title='Sample Property', description='Description', location='Berlin', price=1000,
            room_count=2, property_type='apartment', owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_view_history_recorded(self):
        url = reverse('api:property-detail', kwargs={'pk': self.property.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        history = ViewHistory.objects.filter(user=self.user, property=self.property)
        self.assertEqual(history.count(), 1)


class NotificationTest(APITestCase):
    def setUp(self):
        url = reverse('api:user-list')
        tenant_data = {'username': 'tenant', 'password': 'password123', 'role': 'tenant'}
        landlord_data = {'username': 'landlord', 'password': 'password123', 'role': 'landlord'}
        self.client.post(url, tenant_data)
        self.client.post(url, landlord_data)

        self.landlord = User.objects.get(username='landlord')
        self.tenant = User.objects.get(username='tenant')
        self.property = Property.objects.create(title='Test Property', owner=self.landlord)
        self.client.force_authenticate(user=self.tenant)

    def test_booking_notification_created(self):
        url = reverse('api:booking-list')
        data = {'property': self.property.id, 'start_date': '2024-12-01', 'end_date': '2024-12-10'}
        self.client.post(url, data)
        notification = Notification.objects.filter(recipient=self.landlord, event_type='booking_created')
        self.assertEqual(notification.count(), 1)

    def test_review_notification_created(self):
        url = reverse('api:review-list')
        data = {'property': self.property.id, 'rating': 5, 'comment': 'Great place!'}
        self.client.post(url, data)
        notification = Notification.objects.filter(recipient=self.landlord, event_type='new_review')
        self.assertEqual(notification.count(), 1)
