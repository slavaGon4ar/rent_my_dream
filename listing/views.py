from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from .models import (
    Property,
    Booking,
    Review,
    User,
    SearchHistory,
    ViewHistory,
    Notification
    )
from rest_framework.permissions import IsAuthenticated
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


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        notify_booking_created(booking)  # Уведомление о создании бронирования

    def perform_update(self, serializer):
        booking = serializer.save()
        notify_booking_status_changed(booking)  # Уведомление о смене статуса бронирования


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        notify_new_review(review)  # Уведомление о новом отзыве

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        # Сохраняем историю поиска, если присутствует параметр `search`
        search_query = request.query_params.get('search', None)
        if search_query and request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, keyword=search_query)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Сохраняем историю просмотра при доступе к конкретному объекту
        response = super().retrieve(request, *args, **kwargs)
        if request.user.is_authenticated:
            ViewHistory.objects.create(user=request.user, property=self.get_object())
        return response


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrLandlordBooking]

    def get_queryset(self):
        """
        Ограничиваем список бронирований, которые пользователь может видеть:
        - Tenant может видеть только свои бронирования.
        - Landlord может видеть бронирования только для своих объектов.
        """
        user = self.request.user

        # Пропускаем выполнение, если это запрос на генерацию схемы Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        # Проверка, если запрос идет от анонимного пользователя
        if not user.is_authenticated:
            return Booking.objects.none()

        if user.role == 'tenant':
            return Booking.objects.filter(user=user)

        elif user.role == 'landlord':
            return Booking.objects.filter(property__owner=user)

        return Booking.objects.none()  # Другие пользователи не имеют доступа

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsLandlordOrReadOnly]

    # Подключаем фильтры
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Настройка поиска по ключевым словам в полях title и description
    search_fields = ['title', 'description']

    # Настройка фильтрации
    filterset_fields = {
        'price': ['gte', 'lte'],  # Фильтрация по минимальной и максимальной цене
        'location': ['exact'],  # Фильтрация по местоположению
        'room_count': ['gte', 'lte'],  # Фильтрация по диапазону количества комнат
        'property_type': ['exact'],  # Фильтрация по типу жилья
    }

    # Настройка сортировки
    ordering_fields = ['price', 'created_at']  # Сортировка по цене и дате добавления
    ordering = ['-created_at']  # По умолчанию сортируем по дате добавления (новые сначала)


class SearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пропускаем выполнение при генерации схемы Swagger
        if getattr(self, 'swagger_fake_view', False):
            return SearchHistory.objects.none()

        return SearchHistory.objects.filter(user=self.request.user)


class ViewHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ViewHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пропускаем выполнение при генерации схемы Swagger
        if getattr(self, 'swagger_fake_view', False):
            return ViewHistory.objects.none()

        return ViewHistory.objects.filter(user=self.request.user)

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


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Проверка, если это запрос на генерацию схемы, возвращаем пустой QuerySet
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        # Фильтрация уведомлений для текущего пользователя
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')