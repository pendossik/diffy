"""
Management команда для заполнения БД товарами.

Создаёт 18 товаров:
- 6 ноутбуков
- 6 телевизоров
- 6 планшетов

Использует поиск категорий по подстроке для нахождения нужной категории.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from categories.services import CategoryService
from products.services import ProductService


class Command(BaseCommand):
    help = 'Заполняет БД товарами (ноутбуки, телевизоры, планшеты)'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение БД товарами...')

        # Получаем первого superuser
        superuser = User.objects.filter(role='superuser').first()
        if not superuser:
            self.stderr.write(self.style.ERROR('Superuser не найден!'))
            return

        self.stdout.write(f'Использую пользователя: {superuser.email}')

        # Находим категории по поиску
        try:
            # Ноутбуки
            laptops_categories = CategoryService.get_categories_list(search='ноутбук')
            if not laptops_categories.exists():
                self.stderr.write(self.style.ERROR('Категория "Ноутбук" не найдена!'))
                return
            laptop_category = laptops_categories.first()
            self.stdout.write(f'Найдена категория для ноутбуков: {laptop_category.name} (ID={laptop_category.id})')

            # Телевизоры
            tv_categories = CategoryService.get_categories_list(search='телевизор')
            if not tv_categories.exists():
                self.stderr.write(self.style.ERROR('Категория "Телевизор" не найдена!'))
                return
            tv_category = tv_categories.first()
            self.stdout.write(f'Найдена категория для телевизоров: {tv_category.name} (ID={tv_category.id})')

            # Планшеты
            tablets_categories = CategoryService.get_categories_list(search='планшет')
            if not tablets_categories.exists():
                self.stderr.write(self.style.ERROR('Категория "Планшет" не найдена!'))
                return
            tablet_category = tablets_categories.first()
            self.stdout.write(f'Найдена категория для планшетов: {tablet_category.name} (ID={tablet_category.id})')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка поиска категорий: {str(e)}'))
            return

        # Создаём товары
        products_data = {
            'laptops': [
                {
                    'name': 'Dell XPS 15 9520',
                    'name_ru': 'Dell XPS 15 9520',
                    'name_en': 'Dell XPS 15 9520',
                    'img': 'products/dell-xps-15-9520.jpg',
                },
                {
                    'name': 'MacBook Pro 16 M2 Max',
                    'name_ru': 'MacBook Pro 16 M2 Max',
                    'name_en': 'MacBook Pro 16 M2 Max',
                    'img': 'products/macbook-pro-16-m2.jpg',
                },
                {
                    'name': 'ASUS ROG Zephyrus G14',
                    'name_ru': 'ASUS ROG Zephyrus G14',
                    'name_en': 'ASUS ROG Zephyrus G14',
                    'img': 'products/asus-rog-g14.jpg',
                },
                {
                    'name': 'HP Spectre x360 14',
                    'name_ru': 'HP Spectre x360 14',
                    'name_en': 'HP Spectre x360 14',
                    'img': 'products/hp-spectre-x360.jpg',
                },
                {
                    'name': 'Lenovo ThinkPad X1 Carbon Gen 11',
                    'name_ru': 'Lenovo ThinkPad X1 Carbon Gen 11',
                    'name_en': 'Lenovo ThinkPad X1 Carbon Gen 11',
                    'img': 'products/lenovo-thinkpad-x1.jpg',
                },
                {
                    'name': 'Acer Swift 5 SF514',
                    'name_ru': 'Acer Swift 5 SF514',
                    'name_en': 'Acer Swift 5 SF514',
                    'img': 'products/acer-swift-5.jpg',
                },
            ],
            'tvs': [
                {
                    'name': 'Samsung QN90B Neo QLED 65"',
                    'name_ru': 'Samsung QN90B Neo QLED 65"',
                    'name_en': 'Samsung QN90B Neo QLED 65"',
                    'img': 'products/samsung-qn90b.jpg',
                },
                {
                    'name': 'LG C2 OLED 55"',
                    'name_ru': 'LG C2 OLED 55"',
                    'name_en': 'LG C2 OLED 55"',
                    'img': 'products/lg-c2-oled.jpg',
                },
                {
                    'name': 'Sony A95K QD-OLED 65"',
                    'name_ru': 'Sony A95K QD-OLED 65"',
                    'name_en': 'Sony A95K QD-OLED 65"',
                    'img': 'products/sony-a95k.jpg',
                },
                {
                    'name': 'TCL 6-Series 65R635',
                    'name_ru': 'TCL 6-Series 65R635',
                    'name_en': 'TCL 6-Series 65R635',
                    'img': 'products/tcl-6-series.jpg',
                },
                {
                    'name': 'Hisense U8H ULED 75"',
                    'name_ru': 'Hisense U8H ULED 75"',
                    'name_en': 'Hisense U8H ULED 75"',
                    'img': 'products/hisense-u8h.jpg',
                },
                {
                    'name': 'Philips OLED+937 65"',
                    'name_ru': 'Philips OLED+937 65"',
                    'name_en': 'Philips OLED+937 65"',
                    'img': 'products/philips-oled-937.jpg',
                },
            ],
            'tablets': [
                {
                    'name': 'iPad Pro 12.9" M2',
                    'name_ru': 'iPad Pro 12.9" M2',
                    'name_en': 'iPad Pro 12.9" M2',
                    'img': 'products/ipad-pro-129-m2.jpg',
                },
                {
                    'name': 'Samsung Galaxy Tab S8 Ultra',
                    'name_ru': 'Samsung Galaxy Tab S8 Ultra',
                    'name_en': 'Samsung Galaxy Tab S8 Ultra',
                    'img': 'products/galaxy-tab-s8-ultra.jpg',
                },
                {
                    'name': 'Microsoft Surface Pro 9',
                    'name_ru': 'Microsoft Surface Pro 9',
                    'name_en': 'Microsoft Surface Pro 9',
                    'img': 'products/surface-pro-9.jpg',
                },
                {
                    'name': 'Xiaomi Pad 6 Pro',
                    'name_ru': 'Xiaomi Pad 6 Pro',
                    'name_en': 'Xiaomi Pad 6 Pro',
                    'img': 'products/xiaomi-pad-6-pro.jpg',
                },
                {
                    'name': 'Lenovo Tab P12 Pro',
                    'name_ru': 'Lenovo Tab P12 Pro',
                    'name_en': 'Lenovo Tab P12 Pro',
                    'img': 'products/lenovo-tab-p12-pro.jpg',
                },
                {
                    'name': 'OnePlus Pad',
                    'name_ru': 'OnePlus Pad',
                    'name_en': 'OnePlus Pad',
                    'img': 'products/oneplus-pad.jpg',
                },
            ],
        }

        created_count = 0

        # Создаём ноутбуки
        self.stdout.write('\nСоздаю ноутбуки...')
        for product_data in products_data['laptops']:
            try:
                ProductService.create_product(
                    user=superuser,
                    name=product_data['name'],
                    category_id=laptop_category.id,
                    img=product_data['img'],
                    name_ru=product_data['name_ru'],
                    name_en=product_data['name_en'],
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {product_data["name"]}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  ✗ {product_data["name"]}: {str(e)}'))

        # Создаём телевизоры
        self.stdout.write('\nСоздаю телевизоры...')
        for product_data in products_data['tvs']:
            try:
                ProductService.create_product(
                    user=superuser,
                    name=product_data['name'],
                    category_id=tv_category.id,
                    img=product_data['img'],
                    name_ru=product_data['name_ru'],
                    name_en=product_data['name_en'],
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {product_data["name"]}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  ✗ {product_data["name"]}: {str(e)}'))

        # Создаём планшеты
        self.stdout.write('\nСоздаю планшеты...')
        for product_data in products_data['tablets']:
            try:
                ProductService.create_product(
                    user=superuser,
                    name=product_data['name'],
                    category_id=tablet_category.id,
                    img=product_data['img'],
                    name_ru=product_data['name_ru'],
                    name_en=product_data['name_en'],
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {product_data["name"]}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  ✗ {product_data["name"]}: {str(e)}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Готово! Создано товаров: {created_count}/18'))
