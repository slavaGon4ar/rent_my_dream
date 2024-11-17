from rest_framework import serializers
from .models import (
    User,
    Property,
    Booking,
    Review,
    SearchHistory,
    ViewHistory,
    Category,
    Notification,
)

class PropertySerializer(serializers.ModelSerializer):
    location = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def update(self, instance, validated_data):
        # Удаляем `created_at` из данных, чтобы избежать ошибок при обновлении
        validated_data.pop('created_at', None)
        return super().update(instance, validated_data)

    def validate(self, attrs):
        # Удаляем `created_at` из данных при валидации, если он есть
        attrs.pop('created_at', None)
        return super().validate(attrs)

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
       model = User
       fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'keyword', 'created_at']
        read_only_fields = ['id', 'created_at']

class ViewHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewHistory
        fields = ['id', 'property', 'created_at']
        read_only_fields = ['id', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'event_type', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
