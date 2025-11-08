# для ввода тестовых данных
from django.core.management.base import BaseCommand
from compare.models import Category, Product, Characteristic

class Command(BaseCommand):
    help = "Populate compare app with sample categories, products and characteristics"

    def handle(self, *args, **options):
        # Очистим старые тестовые данные (опционально)
        Characteristic.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Категории
        cats = [
            "Смартфоны",
            "Ноутбуки",
            "Планшеты",
        ]
        categories = {}
        for name in cats:
            c, _ = Category.objects.get_or_create(name=name)
            categories[name] = c
            self.stdout.write(self.style.SUCCESS(f"Категория создана: {name}"))

        # Продукты и их характеристики
        products_data = [
            {
                "name": "Phone A",
                "category": categories["Смартфоны"],
                "characteristics": [
                    ("Экран", "6.1\" OLED"),
                    ("Процессор", "Octa-core 2.9GHz"),
                    ("Память", "8 GB"),
                    ("Аккумулятор", "3500 mAh"),
                ],
            },
            {
                "name": "Phone B",
                "category": categories["Смартфоны"],
                "characteristics": [
                    ("Экран", "6.7\" AMOLED"),
                    ("Процессор", "Octa-core 3.1GHz"),
                    ("Память", "12 GB"),
                    ("Аккумулятор", "4500 mAh"),
                ],
            },
            {
                "name": "Laptop X",
                "category": categories["Ноутбуки"],
                "characteristics": [
                    ("Экран", "15.6\" IPS"),
                    ("Процессор", "Intel i7"),
                    ("ОЗУ", "16 GB"),
                    ("SSD", "512 GB"),
                ],
            },
            {
                "name": "Tablet Z",
                "category": categories["Планшеты"],
                "characteristics": [
                    ("Экран", "11\""),
                    ("Память", "6 GB"),
                    ("Аккумулятор", "8000 mAh"),
                ],
            },
        ]

        for p in products_data:
            prod = Product.objects.create(name=p["name"], category=p["category"])
            for ch_name, ch_value in p["characteristics"]:
                Characteristic.objects.create(product=prod, name=ch_name, value=ch_value)
            self.stdout.write(self.style.SUCCESS(f"Продукт создан: {prod.name}"))

        self.stdout.write(self.style.SUCCESS("Заполнение тестовыми данными завершено."))
