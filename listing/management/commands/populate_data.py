import random
from django.core.management.base import BaseCommand
from listing.models import User, Property, Category

class Command(BaseCommand):
    help = 'Создает тестовые данные для пользователей и объектов жилья'

    def handle(self, *args, **kwargs):
        # Создание тестовых пользователей (собственников)
        landlords = []
        for i in range(7):  # Создаст 7 собственников
            username = f'landlord{i+1}'
            email = f'landlord{i+1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='landlord'
            )
            landlords.append(user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {username}'))

        # Создание категорий
        categories = ['Эконом', 'Бизнес', 'Люкс']
        category_objects = [Category.objects.create(name=cat) for cat in categories]

        # Создание тестовых объектов жилья
        property_types = ['apartment', 'house', 'studio']
        locations = ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt']

        for i in range(100):  # Создаст 100 объектов жилья
            prop = Property.objects.create(
                title=f'Объект {i+1}',
                description=f'Описание объекта {i+1} с уникальными характеристиками.',
                location=random.choice(locations),
                price=random.randint(500, 3000),
                room_count=random.randint(1, 5),
                property_type=random.choice(property_types),
                status='active',
                views=random.randint(0, 100),
                owner=random.choice(landlords)
            )
            # Назначение случайных категорий
            prop.categories.add(*random.sample(category_objects, random.randint(1, 3)))
            prop.save()
            self.stdout.write(self.style.SUCCESS(f'Создан объект жилья: {prop.title}'))
