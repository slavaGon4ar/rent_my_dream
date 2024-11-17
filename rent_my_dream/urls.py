from django.contrib import admin
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from listing.views import (
    PropertyViewSet,
    BookingViewSet,
    ReviewViewSet,
    UserViewSet,
    SearchHistoryViewSet,
    ViewHistoryViewSet,
    NotificationViewSet
)

# Настройка схемы Swagger для документации API
schema_view = get_schema_view(
    openapi.Info(
        title="Rent My Dream API",
        default_version='v1',
        description="API documentation for rent_my_dream",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Настройка маршрутов для ViewSets
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='properties')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'users', UserViewSet, basename='user-list')
router.register(r'search-history', SearchHistoryViewSet, basename='search-history')
router.register(r'view-history', ViewHistoryViewSet, basename='view-history')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(([
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('', include(router.urls)),
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ], 'api'), namespace='api')),
]

# Подключение debug_toolbar при DEBUG=True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
