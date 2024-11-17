# listing/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLandlordOrReadOnly(BasePermission):
    """
    Разрешает доступ к методам POST, PUT, PATCH и DELETE только для пользователей с ролью 'landlord'
    и только для их собственных объектов.
    Доступ на чтение доступен всем пользователям, включая неавторизованных.
    """

    def has_permission(self, request, view):
        # Разрешаем доступ на чтение (GET-запросы) всем пользователям, включая неавторизованных
        if request.method in SAFE_METHODS:
            return True

        # Проверяем, что у пользователя есть роль 'landlord' для создания, обновления и удаления
        return request.user.is_authenticated and request.user.role == 'landlord'

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ на чтение (GET-запросы) всем пользователям, включая неавторизованных
        if request.method in SAFE_METHODS:
            return True

        # Проверяем, что пользователь - владелец объекта и имеет роль 'landlord'
        return obj.owner == request.user and request.user.role == 'landlord'


class IsOwnerOrLandlordBooking(BasePermission):
    """
    Разрешение, позволяющее пользователям с ролью 'tenant' управлять только своими бронированиями,
    а пользователям с ролью 'landlord' — управлять бронированиями только для их объектов.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для владельца бронирования или владельца объекта
        if request.method in SAFE_METHODS:
            if request.user.role == 'tenant':
                # Tenant может просматривать только свои бронирования
                return obj.user == request.user
            elif request.user.role == 'landlord':
                # Landlord может просматривать бронирования для своих объектов
                return obj.property.owner == request.user

        # Проверка на уровне изменения объекта (PATCH, DELETE)
        # Tenant может редактировать и удалять только свои бронирования
        if request.user.role == 'tenant':
            return obj.user == request.user

        # Landlord может редактировать и удалять только бронирования своих объектов
        elif request.user.role == 'landlord':
            return obj.property.owner == request.user

        return False


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Разрешение, которое позволяет доступ к методам GET (чтение) для всех пользователей,
    а для остальных методов требует авторизации.
    """

    def has_permission(self, request, view):
        # Разрешаем доступ к методам чтения (GET) для всех пользователей
        if request.method in SAFE_METHODS:
            return True

        # Для остальных методов требуется авторизация
        return request.user.is_authenticated

class IsOwnerOrReadOnly(BasePermission):
    """
    Позволяет доступ к объекту только его владельцу для редактирования.
    Просмотр разрешен всем пользователям.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user