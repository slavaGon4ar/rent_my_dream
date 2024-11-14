import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from listing.models import User, Property, Category, Booking, Review, SearchHistory, ViewHistory, Notification


class Command(BaseCommand):
    help = 'Очистка старых данных и создание новых тестовых данных для пользователей и объектов жилья'

    def handle(self, *args, **kwargs):
        # Очистка данных
        self.stdout.write(self.style.WARNING('Удаление старых данных...'))
        Notification.objects.all().delete()
        ViewHistory.objects.all().delete()
        SearchHistory.objects.all().delete()
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Property.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Удаляет всех пользователей, кроме суперпользователей
        self.stdout.write(self.style.SUCCESS('Все данные успешно очищены.'))

        # Создание тестовых пользователей (собственников и арендаторов)
        landlords = []
        tenants = []

        # Создание собственников
        for i in range(7):  # Создаст 7 собственников
            username = f'landlord{i + 1}'
            email = f'landlord{i + 1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='landlord'
            )
            landlords.append(user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь-собственник: {username}'))

        # Создание арендаторов
        for i in range(10):  # Создаст 10 арендаторов
            username = f'tenant{i + 1}'
            email = f'tenant{i + 1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='tenant'
            )
            tenants.append(user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь-арендатор: {username}'))

        # Создание категорий
        categories = ['Эконом', 'Бизнес', 'Люкс']
        category_objects = [Category.objects.create(name=cat) for cat in categories]

        # Создание тестовых объектов жилья
        property_types = ['apartment', 'house', 'studio']
        locations = ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt']

        properties = []
        for i in range(100):  # Создаст 100 объектов жилья
            prop = Property.objects.create(
                title=f'Объект {i + 1}',
                description=f'Описание объекта {i + 1} с уникальными характеристиками.',
                location=random.choice(locations),
                price=random.randint(500, 3000),
                room_count=random.randint(1, 5),
                property_type=random.choice(property_types),
                status='active',
                views=random.randint(0, 100),
                owner=random.choice(landlords)
            )
            prop.categories.add(*random.sample(category_objects, random.randint(1, 3)))
            prop.save()
            properties.append(prop)
            self.stdout.write(self.style.SUCCESS(f'Создан объект жилья: {prop.title}'))

        # Создание бронирований для арендаторов
        for tenant in tenants:
            prop = random.choice(properties)
            booking = Booking.objects.create(
                property=prop,
                user=tenant,
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timezone.timedelta(days=random.randint(1, 14))).date(),
                status=random.choice(['pending', 'confirmed', 'canceled'])
            )
            self.stdout.write(self.style.SUCCESS(f'Создано бронирование для {tenant.username} на объект {prop.title}'))

        # Создание отзывов
        for tenant in tenants:
            prop = random.choice(properties)
            review = Review.objects.create(
                property=prop,
                user=tenant,
                rating=random.randint(1, 5),
                comment=f'Отзыв от {tenant.username} на объект {prop.title}.',
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f'Создан отзыв от {tenant.username} для объекта {prop.title}'))

        # Создание истории поиска
        for tenant in tenants:
            search_keywords = ['Berlin', 'house', 'apartment', 'cheap', 'luxury']
            search = SearchHistory.objects.create(
                user=tenant,
                keyword=random.choice(search_keywords),
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(
                f'Создана запись истории поиска для {tenant.username} по ключевому слову "{search.keyword}"'))

        # Создание истории просмотров
        for tenant in tenants:
            prop = random.choice(properties)
            view = ViewHistory.objects.create(
                user=tenant,
                property=prop,
                created_at=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(f'Создана запись истории просмотра для {tenant.username} на объект {prop.title}'))

        # Создание уведомлений
        for landlord in landlords:
            notification = Notification.objects.create(
                recipient=landlord,
                message='У вас новое бронирование!',
                event_type='booking_created',
                created_at=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(f'Создано уведомление для {landlord.username}: "{notification.message}"'))


import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from listing.models import User, Property, Category, Booking, Review, SearchHistory, ViewHistory, Notification


class Command(BaseCommand):
    help = 'Очистка старых данных и создание новых тестовых данных для пользователей и объектов жилья'

    def handle(self, *args, **kwargs):
        # Очистка данных
        self.stdout.write(self.style.WARNING('Удаление старых данных...'))
        Notification.objects.all().delete()
        ViewHistory.objects.all().delete()
        SearchHistory.objects.all().delete()
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Property.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Удаляет всех пользователей, кроме суперпользователей
        self.stdout.write(self.style.SUCCESS('Все данные успешно очищены.'))

        # Создание тестовых пользователей (собственников и арендаторов)
        landlords = []
        tenants = []

        # Создание собственников
        for i in range(7):  # Создаст 7 собственников
            username = f'landlord{i + 1}'
            email = f'landlord{i + 1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='landlord'
            )
            landlords.append(user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь-собственник: {username}'))

        # Создание арендаторов
        for i in range(10):  # Создаст 10 арендаторов
            username = f'tenant{i + 1}'
            email = f'tenant{i + 1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='tenant'
            )
            tenants.append(user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь-арендатор: {username}'))

        # Создание категорий
        categories = ['Эконом', 'Бизнес', 'Люкс']
        category_objects = [Category.objects.create(name=cat) for cat in categories]

        # Создание тестовых объектов жилья
        property_types = ['apartment', 'house', 'studio']
        locations = ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt']

        properties = []
        for i in range(100):  # Создаст 100 объектов жилья
            prop = Property.objects.create(
                title=f'Объект {i + 1}',
                description=f'Описание объекта {i + 1} с уникальными характеристиками.',
                location=random.choice(locations),
                price=random.randint(500, 3000),
                room_count=random.randint(1, 5),
                property_type=random.choice(property_types),
                status='active',
                views=random.randint(0, 100),
                owner=random.choice(landlords)
            )
            prop.categories.add(*random.sample(category_objects, random.randint(1, 3)))
            prop.save()
            properties.append(prop)
            self.stdout.write(self.style.SUCCESS(f'Создан объект жилья: {prop.title}'))

        # Создание бронирований для арендаторов
        for tenant in tenants:
            prop = random.choice(properties)
            booking = Booking.objects.create(
                property=prop,
                user=tenant,
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timezone.timedelta(days=random.randint(1, 14))).date(),
                status=random.choice(['pending', 'confirmed', 'canceled'])
            )
            self.stdout.write(self.style.SUCCESS(f'Создано бронирование для {tenant.username} на объект {prop.title}'))

        # Создание отзывов
        for tenant in tenants:
            prop = random.choice(properties)
            review = Review.objects.create(
                property=prop,
                user=tenant,
                rating=random.randint(1, 5),
                comment=f'Отзыв от {tenant.username} на объект {prop.title}.',
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f'Создан отзыв от {tenant.username} для объекта {prop.title}'))

        # Создание истории поиска
        for tenant in tenants:
            search_keywords = ['Berlin', 'house', 'apartment', 'cheap', 'luxury']
            search = SearchHistory.objects.create(
                user=tenant,
                keyword=random.choice(search_keywords),
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(
                f'Создана запись истории поиска для {tenant.username} по ключевому слову "{search.keyword}"'))

        # Создание истории просмотров
        for tenant in tenants:
            prop = random.choice(properties)
            view = ViewHistory.objects.create(
                user=tenant,
                property=prop,
                created_at=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(f'Создана запись истории просмотра для {tenant.username} на объект {prop.title}'))

        # Создание уведомлений
        for landlord in landlords:
            notification = Notification.objects.create(
                recipient=landlord,
                event_type='booking_created',
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f'Создано уведомление для {landlord.username}'))

