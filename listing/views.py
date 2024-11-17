from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from listing.models import Property, Booking, Review, User, SearchHistory, ViewHistory, Notification
from listing.serializers import PropertySerializer, BookingSerializer, ReviewSerializer, UserSerializer, SearchHistorySerializer, ViewHistorySerializer, NotificationSerializer


from .models import (
    Property,
    Booking,
    Review,
    User,
    SearchHistory,
    ViewHistory,
    Notification
)
from .serializers import (
    PropertySerializer,
    BookingSerializer,
    ReviewSerializer,
    UserSerializer,
    SearchHistorySerializer,
    ViewHistorySerializer,
    NotificationSerializer
)
from .permissions import (
    IsLandlordOrReadOnly,
    IsOwnerOrLandlordBooking,
    IsAuthenticatedOrReadOnly,
    IsOwnerOrReadOnly
)
from .notifications import (
    notify_booking_created,
    notify_booking_status_changed,
    notify_new_review
)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsLandlordOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'description']
    filterset_fields = {
        'price': ['gte', 'lte'],
        'location': ['exact'],
        'room_count': ['gte', 'lte'],
        'property_type': ['exact'],
    }
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', None)
        if search_query and request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, keyword=search_query)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        if request.user.is_authenticated:
            ViewHistory.objects.create(user=request.user, property=self.get_object())
        return response


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrLandlordBooking]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        notify_booking_created(booking)

    def perform_update(self, serializer):
        booking = serializer.save()
        notify_booking_status_changed(booking)

    def get_queryset(self):
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        if not user.is_authenticated:
            return Booking.objects.none()

        if user.role == 'tenant':
            return Booking.objects.filter(user=user)

        elif user.role == 'landlord':
            return Booking.objects.filter(property__owner=user)

        return Booking.objects.none()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        notify_new_review(review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SearchHistory.objects.none()
        return SearchHistory.objects.filter(user=self.request.user)


class ViewHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ViewHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ViewHistory.objects.none()
        return ViewHistory.objects.filter(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


def notify_booking_created(booking):
    content = f'New booking created by {booking.user.username} for property {booking.property.title}.'
    Notification.objects.create(
        recipient=booking.property.owner,
        event_type='booking_created',
        content=content,
        related_object_id=booking.id
    )


def notify_booking_status_changed(booking):
    content = f'Booking status changed to {booking.status} for property {booking.property.title}.'
    Notification.objects.create(
        recipient=booking.user,
        event_type='booking_status_changed',
        content=content,
        related_object_id=booking.id
    )


def notify_new_review(review):
    content = f'New review from {review.user.username} on property {review.property.title}.'
    Notification.objects.create(
        recipient=review.property.owner,
        event_type='new_review',
        content=content,
        related_object_id=review.id
    )
