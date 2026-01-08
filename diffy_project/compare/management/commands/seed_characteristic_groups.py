from django.core.management.base import BaseCommand
from compare.models import Category, CharacteristicGroup

SMARTPHONE_GROUPS = [
    {"order": 1, "name": "Размеры"},
    {"order": 2, "name": "Корпус"},
    {"order": 3, "name": "Дисплей"},
    {"order": 4, "name": "Процессор"},
    {"order": 5, "name": "Батарея"},
    {"order": 6, "name": "Основная камера"},
    {"order": 7, "name": "Фронтальная камера"},
    {"order": 8, "name": "Операционная система"},
    {"order": 9, "name": "Bluetooth"},
]

class Command(BaseCommand):
    help = "Создаёт группы характеристик для смартфонов"

    def handle(self, *args, **kwargs):
        try:
            category = Category.objects.get(name="Смартфоны")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Категория 'Смартфоны' отсутствует"))
            return

        for g in SMARTPHONE_GROUPS:
            obj, created = CharacteristicGroup.objects.get_or_create(
                category=category,
                name=g["name"],
                defaults={"order": g["order"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлено: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Уже существует: {obj.name}"))
