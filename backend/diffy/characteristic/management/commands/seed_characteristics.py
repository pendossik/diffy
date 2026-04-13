"""
Management команда для заполнения БД группами характеристик и шаблонами.

Создаёт:
- 3 группы характеристик для каждой категории (Ноутбук, Телевизор, Планшет)
- 2 шаблона характеристик в каждой группе
- Заполняет значения характеристик для всех 18 товаров

Использует поиск категорий по подстроке.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from categories.services import CategoryService
from characteristic.services import (
    CharacteristicGroupService,
    CharacteristicTemplateService,
    CharacteristicValueService,
)
from characteristic.models import CharacteristicGroup, CharacteristicTemplate
from products.models import Product


class Command(BaseCommand):
    help = 'Заполняет БД группами характеристик, шаблонами и значениями'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение БД характеристиками...')

        # Получаем первого superuser
        superuser = User.objects.filter(role='superuser').first()
        if not superuser:
            self.stderr.write(self.style.ERROR('Superuser не найден!'))
            return

        self.stdout.write(f'Использую пользователя: {superuser.email}')

        # Находим категории
        try:
            laptops_categories = CategoryService.get_categories_list(search='ноутбук')
            tv_categories = CategoryService.get_categories_list(search='телевизор')
            tablets_categories = CategoryService.get_categories_list(search='планшет')

            if not laptops_categories.exists() or not tv_categories.exists() or not tablets_categories.exists():
                self.stderr.write(self.style.ERROR('Одна или несколько категорий не найдены!'))
                return

            laptop_category = laptops_categories.first()
            tv_category = tv_categories.first()
            tablet_category = tablets_categories.first()

            self.stdout.write(f'Категории найдены:')
            self.stdout.write(f'  - Ноутбуки: {laptop_category.name} (ID={laptop_category.id})')
            self.stdout.write(f'  - Телевизоры: {tv_category.name} (ID={tv_category.id})')
            self.stdout.write(f'  - Планшеты: {tablet_category.name} (ID={tablet_category.id})')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка поиска категорий: {str(e)}'))
            return

        # Определяем группы характеристик для каждой категории
        groups_config = {
            'laptops': {
                'category': laptop_category,
                'groups': [
                    {
                        'name': 'Основные',
                        'name_ru': 'Основные',
                        'name_en': 'Basic',
                        'order': 0,
                        'templates': [
                            {'name': 'Процессор', 'name_ru': 'Процессор', 'name_en': 'Processor', 'order': 0},
                            {'name': 'Оперативная память', 'name_ru': 'Оперативная память', 'name_en': 'RAM', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Дисплей',
                        'name_ru': 'Дисплей',
                        'name_en': 'Display',
                        'order': 1,
                        'templates': [
                            {'name': 'Диагональ', 'name_ru': 'Диагональ', 'name_en': 'Screen Size', 'order': 0},
                            {'name': 'Разрешение', 'name_ru': 'Разрешение', 'name_en': 'Resolution', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Накопитель',
                        'name_ru': 'Накопитель',
                        'name_en': 'Storage',
                        'order': 2,
                        'templates': [
                            {'name': 'Тип накопителя', 'name_ru': 'Тип накопителя', 'name_en': 'Storage Type', 'order': 0},
                            {'name': 'Объём SSD', 'name_ru': 'Объём SSD', 'name_en': 'SSD Capacity', 'order': 1},
                        ]
                    },
                ]
            },
            'tvs': {
                'category': tv_category,
                'groups': [
                    {
                        'name': 'Экран',
                        'name_ru': 'Экран',
                        'name_en': 'Screen',
                        'order': 0,
                        'templates': [
                            {'name': 'Диагональ', 'name_ru': 'Диагональ', 'name_en': 'Screen Size', 'order': 0},
                            {'name': 'Технология', 'name_ru': 'Технология', 'name_en': 'Technology', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Изображение',
                        'name_ru': 'Изображение',
                        'name_en': 'Picture',
                        'order': 1,
                        'templates': [
                            {'name': 'Разрешение', 'name_ru': 'Разрешение', 'name_en': 'Resolution', 'order': 0},
                            {'name': 'HDR', 'name_ru': 'HDR', 'name_en': 'HDR', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Smart TV',
                        'name_ru': 'Smart TV',
                        'name_en': 'Smart TV',
                        'order': 2,
                        'templates': [
                            {'name': 'ОС', 'name_ru': 'ОС', 'name_en': 'OS', 'order': 0},
                            {'name': 'Wi-Fi', 'name_ru': 'Wi-Fi', 'name_en': 'Wi-Fi', 'order': 1},
                        ]
                    },
                ]
            },
            'tablets': {
                'category': tablet_category,
                'groups': [
                    {
                        'name': 'Основные',
                        'name_ru': 'Основные',
                        'name_en': 'Basic',
                        'order': 0,
                        'templates': [
                            {'name': 'Процессор', 'name_ru': 'Процессор', 'name_en': 'Processor', 'order': 0},
                            {'name': 'Оперативная память', 'name_ru': 'Оперативная память', 'name_en': 'RAM', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Дисплей',
                        'name_ru': 'Дисплей',
                        'name_en': 'Display',
                        'order': 1,
                        'templates': [
                            {'name': 'Диагональ', 'name_ru': 'Диагональ', 'name_en': 'Screen Size', 'order': 0},
                            {'name': 'Разрешение', 'name_ru': 'Разрешение', 'name_en': 'Resolution', 'order': 1},
                        ]
                    },
                    {
                        'name': 'Питание',
                        'name_ru': 'Питание',
                        'name_en': 'Battery',
                        'order': 2,
                        'templates': [
                            {'name': 'Ёмкость батареи', 'name_ru': 'Ёмкость батареи', 'name_en': 'Battery Capacity', 'order': 0},
                            {'name': 'Быстрая зарядка', 'name_ru': 'Быстрая зарядка', 'name_en': 'Fast Charging', 'order': 1},
                        ]
                    },
                ]
            },
        }

        # Значения характеристик для товаров (по 3 группы на товар)
        products_characteristics = {
            'laptops': [
                # Dell XPS 15 9520
                [
                    {'group_idx': 0, 'values': ['Intel Core i7-12700H', '16 ГБ']},
                    {'group_idx': 1, 'values': ['15.6 дюймов', '3840x2400']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '512 ГБ']},
                ],
                # MacBook Pro 16 M2 Max
                [
                    {'group_idx': 0, 'values': ['Apple M2 Max', '32 ГБ']},
                    {'group_idx': 1, 'values': ['16.2 дюйма', '3456x2234']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '1 ТБ']},
                ],
                # ASUS ROG Zephyrus G14
                [
                    {'group_idx': 0, 'values': ['AMD Ryzen 9 6900HS', '16 ГБ']},
                    {'group_idx': 1, 'values': ['14 дюймов', '2560x1440']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '1 ТБ']},
                ],
                # HP Spectre x360 14
                [
                    {'group_idx': 0, 'values': ['Intel Core i7-1255U', '16 ГБ']},
                    {'group_idx': 1, 'values': ['13.5 дюймов', '3000x2000']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '512 ГБ']},
                ],
                # Lenovo ThinkPad X1 Carbon Gen 11
                [
                    {'group_idx': 0, 'values': ['Intel Core i7-1355U', '16 ГБ']},
                    {'group_idx': 1, 'values': ['14 дюймов', '2880x1800']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '512 ГБ']},
                ],
                # Acer Swift 5 SF514
                [
                    {'group_idx': 0, 'values': ['Intel Core i5-1235U', '8 ГБ']},
                    {'group_idx': 1, 'values': ['14 дюймов', '1920x1080']},
                    {'group_idx': 2, 'values': ['SSD NVMe', '256 ГБ']},
                ],
            ],
            'tvs': [
                # Samsung QN90B
                [
                    {'group_idx': 0, 'values': ['65 дюймов', 'Neo QLED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'HDR10+']},
                    {'group_idx': 2, 'values': ['Tizen', 'Есть']},
                ],
                # LG C2 OLED
                [
                    {'group_idx': 0, 'values': ['55 дюймов', 'OLED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'Dolby Vision']},
                    {'group_idx': 2, 'values': ['webOS', 'Есть']},
                ],
                # Sony A95K
                [
                    {'group_idx': 0, 'values': ['65 дюймов', 'QD-OLED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'Dolby Vision']},
                    {'group_idx': 2, 'values': ['Google TV', 'Есть']},
                ],
                # TCL 6-Series
                [
                    {'group_idx': 0, 'values': ['65 дюймов', 'Mini LED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'HDR10']},
                    {'group_idx': 2, 'values': ['Roku TV', 'Есть']},
                ],
                # Hisense U8H
                [
                    {'group_idx': 0, 'values': ['75 дюймов', 'ULED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'Dolby Vision']},
                    {'group_idx': 2, 'values': ['Google TV', 'Есть']},
                ],
                # Philips OLED+937
                [
                    {'group_idx': 0, 'values': ['65 дюймов', 'OLED']},
                    {'group_idx': 1, 'values': ['3840x2160', 'HDR10+']},
                    {'group_idx': 2, 'values': ['Android TV', 'Есть']},
                ],
            ],
            'tablets': [
                # iPad Pro 12.9 M2
                [
                    {'group_idx': 0, 'values': ['Apple M2', '8 ГБ']},
                    {'group_idx': 1, 'values': ['12.9 дюймов', '2732x2048']},
                    {'group_idx': 2, 'values': ['10090 мАч', 'Есть']},
                ],
                # Galaxy Tab S8 Ultra
                [
                    {'group_idx': 0, 'values': ['Snapdragon 8 Gen 1', '12 ГБ']},
                    {'group_idx': 1, 'values': ['14.6 дюймов', '2960x1848']},
                    {'group_idx': 2, 'values': ['11200 мАч', 'Есть']},
                ],
                # Surface Pro 9
                [
                    {'group_idx': 0, 'values': ['Intel Core i5-1235U', '8 ГБ']},
                    {'group_idx': 1, 'values': ['13 дюймов', '2880x1920']},
                    {'group_idx': 2, 'values': ['4770 мАч', 'Есть']},
                ],
                # Xiaomi Pad 6 Pro
                [
                    {'group_idx': 0, 'values': ['Snapdragon 8+ Gen 1', '8 ГБ']},
                    {'group_idx': 1, 'values': ['11 дюймов', '2880x1800']},
                    {'group_idx': 2, 'values': ['8600 мАч', 'Есть']},
                ],
                # Lenovo Tab P12 Pro
                [
                    {'group_idx': 0, 'values': ['Snapdragon 870', '8 ГБ']},
                    {'group_idx': 1, 'values': ['12.6 дюймов', '2560x1600']},
                    {'group_idx': 2, 'values': ['10200 мАч', 'Есть']},
                ],
                # OnePlus Pad
                [
                    {'group_idx': 0, 'values': ['MediaTek Dimensity 9000', '8 ГБ']},
                    {'group_idx': 1, 'values': ['11.61 дюймов', '2800x2000']},
                    {'group_idx': 2, 'values': ['9510 мАч', 'Есть']},
                ],
            ],
        }

        created_groups = 0
        created_templates = 0
        created_values = 0

        for category_key, config in groups_config.items():
            category = config['category']
            self.stdout.write(f'\nЗаполняю характеристики для категории: {category.name}')

            # Получаем или создаём группы и шаблоны
            created_group_ids = []
            for group_data in config['groups']:
                # Пытаемся найти существующую группу
                group = CharacteristicGroup.objects.filter(
                    category=category,
                    name=group_data['name']
                ).first()
                
                if not group:
                    # Создаём новую если не существует
                    try:
                        group = CharacteristicGroupService.create_group(
                            user=superuser,
                            category_id=category.id,
                            name=group_data['name'],
                            name_ru=group_data['name_ru'],
                            name_en=group_data['name_en'],
                            order=group_data['order'],
                        )
                        created_groups += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Группа: {group.name}'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'  ✗ Группа "{group_data["name"]}": {str(e)}'))
                        continue
                else:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Группа: {group.name} (существует)'))
                
                created_group_ids.append(group.id)

                # Создаём шаблоны
                for template_data in group_data['templates']:
                    # Пытаемся найти существующий шаблон
                    template = CharacteristicTemplate.objects.filter(
                        group=group,
                        name=template_data['name']
                    ).first()
                    
                    if not template:
                        try:
                            template = CharacteristicTemplateService.create_template(
                                user=superuser,
                                group_id=group.id,
                                name=template_data['name'],
                                name_ru=template_data['name_ru'],
                                name_en=template_data['name_en'],
                                order=template_data['order'],
                            )
                            created_templates += 1
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f'    ✗ Шаблон "{template_data["name"]}": {str(e)}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Шаблон: {template.name} (существует)'))

            # Получаем товары этой категории
            products = list(Product.objects.filter(category=category).order_by('id'))
            characteristics_data = products_characteristics[category_key]

            if len(products) != len(characteristics_data):
                self.stderr.write(self.style.ERROR(f'  ⚠ Количество товаров ({len(products)}) не совпадает с данными ({len(characteristics_data)})'))
                continue

            # Заполняем характеристики для каждого товара
            self.stdout.write(f'  Заполняю характеристики для {len(products)} товаров...')
            for product_idx, product in enumerate(products):
                product_groups = characteristics_data[product_idx]  # Список из 3 групп для этого товара
                
                # Для каждой группы создаём значения
                for group_data in product_groups:
                    group_idx = group_data['group_idx']
                    values = group_data['values']
                    group_id = created_group_ids[group_idx]
                    
                    # Получаем шаблоны этой группы
                    group_templates = list(CharacteristicTemplateService.get_templates_by_group(group_id))
                    
                    # Создаём значения для каждого шаблона
                    for template_idx, template in enumerate(group_templates):
                        if template_idx < len(values):
                            try:
                                value = values[template_idx]
                                CharacteristicValueService.create_value(
                                    user=superuser,
                                    product_id=product.id,
                                    template_id=template.id,
                                    value=value,
                                    value_ru=value,
                                    value_en=value,
                                )
                                created_values += 1
                            except Exception as e:
                                self.stderr.write(self.style.ERROR(f'    ✗ {product.name} - {template.name}: {str(e)}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Готово!'))
        self.stdout.write(self.style.SUCCESS(f'  Групп создано: {created_groups}'))
        self.stdout.write(self.style.SUCCESS(f'  Шаблонов создано: {created_templates}'))
        self.stdout.write(self.style.SUCCESS(f'  Значений создано: {created_values}'))
