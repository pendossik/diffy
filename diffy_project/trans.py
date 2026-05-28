from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate, Product

# 1. Справочник Категорий (Category)
categories_data = {
    1: {"name": "Смартфоны", "name_ru": "Смартфоны", "name_en": "Smartphones"},
    2: {"name": "Планшеты", "name_ru": "Планшеты", "name_en": "Tablets"},
    3: {"name": "Ноутбуки", "name_ru": "Ноутбуки", "name_en": "Laptops"},
    5: {"name": "Консоли", "name_ru": "Консоли", "name_en": "Consoles"},
}

# 2. Справочник Групп характеристик (CharacteristicGroup)
groups_data = {
    10: {"name": "Экран", "name_ru": "Экран", "name_en": "Display"},
    11: {"name": "Процессор", "name_ru": "Процессор", "name_en": "Processor"},
    12: {"name": "Память", "name_ru": "Память", "name_en": "Memory"},
    13: {"name": "Камера", "name_ru": "Камера", "name_en": "Camera"},
    14: {"name": "Батарея", "name_ru": "Батарея", "name_en": "Battery"},
    15: {"name": "Связь", "name_ru": "Связь", "name_en": "Connectivity"},
    16: {"name": "Операционная система", "name_ru": "Операционная система", "name_en": "Operating System"},
    17: {"name": "Корпус", "name_ru": "Корпус", "name_en": "Body"},
    18: {"name": "Прочее", "name_ru": "Прочее", "name_en": "Other"},
    21: {"name": "Ремешок и дисплей", "name_ru": "Ремешок и дисплей", "name_en": "Strap & Display"},
    22: {"name": "Функции и батарея", "name_ru": "Функции и батарея", "name_en": "Features & Battery"},
}

# 3. Справочник Шаблонов характеристик (CharacteristicTemplate)
templates_data = {
    1: {"name": "Тип матрицы", "name_ru": "Тип матрицы", "name_en": "Display Type"},
    2: {"name": "Диагональ экрана", "name_ru": "Диагональ экрана", "name_en": "Screen Size"},
    3: {"name": "Разрешение экрана", "name_ru": "Разрешение экрана", "name_en": "Screen Resolution"},
    4: {"name": "Частота обновления", "name_ru": "Частота обновления", "name_en": "Refresh Rate"},
    5: {"name": "Процессор", "name_ru": "Процессор", "name_en": "Processor Model"},
    6: {"name": "Количество ядер", "name_ru": "Количество ядер", "name_en": "Cores"},
    7: {"name": "Техпроцесс", "name_ru": "Техпроцесс", "name_en": "Lithography"},
    8: {"name": "Оперативная память (RAM)", "name_ru": "Оперативная память (RAM)", "name_en": "RAM"},
    9: {"name": "Встроенная память", "name_ru": "Встроенная память", "name_en": "Storage"},
    10: {"name": "Тип встроенной памяти", "name_ru": "Тип встроенной памяти", "name_en": "Storage Type"},
    11: {"name": "Слот для карты памяти", "name_ru": "Слот для карты памяти", "name_en": "Memory Card Slot"},
    12: {"name": "Тип карты памяти", "name_ru": "Тип карты памяти", "name_en": "Memory Card Type"},
    13: {"name": "Максимальный объем карты памяти", "name_ru": "Максимальный объем карты памяти", "name_en": "Max Memory Card Capacity"},
    14: {"name": "Тип оперативной памяти", "name_ru": "Тип оперативной памяти", "name_en": "RAM Type"},
    15: {"name": "Основная камера", "name_ru": "Основная камера", "name_en": "Main Camera"},
    16: {"name": "Фронтальная камера", "name_ru": "Фронтальная камера", "name_en": "Front Camera"},
    17: {"name": "Емкость аккумулятора", "name_ru": "Емкость аккумулятора", "name_en": "Battery Capacity"},
    18: {"name": "Стандарты связи", "name_ru": "Стандарты связи", "name_en": "Mobile Network"},
    19: {"name": "Поддержка 5G", "name_ru": "Поддержка 5G", "name_en": "5G Support"},
    20: {"name": "Версия Bluetooth", "name_ru": "Версия Bluetooth", "name_en": "Bluetooth Version"},
    21: {"name": "Операционная система", "name_ru": "Операционная система", "name_en": "Operating System"},
    22: {"name": "Материал корпуса", "name_ru": "Материал корпуса", "name_en": "Body Material"},
    23: {"name": "Вес устройства", "name_ru": "Вес устройства", "name_en": "Weight"},
    28: {"name": "Тип дисплея", "name_ru": "Тип дисплея", "name_en": "Display Type"},
    29: {"name": "Диагональ дисплея", "name_ru": "Диагональ дисплея", "name_en": "Display Size"},
    30: {"name": "Емкость аккумулятора", "name_ru": "Емкость аккумулятора", "name_en": "Battery Capacity"},
    31: {"name": "Мониторинг активности", "name_ru": "Мониторинг активности", "name_en": "Activity Monitoring"},
}

# 4. Справочник Товаров (Product)
products_data = {
    5: {"name": "iPhone 17 Pro Max", "name_ru": "iPhone 17 Pro Max", "name_en": "iPhone 17 Pro Max"},
    6: {"name": "iPhone Air", "name_ru": "iPhone Air", "name_en": "iPhone Air"},
    7: {"name": "Samsung Galaxy S25 Ultra", "name_ru": "Samsung Galaxy S25 Ultra", "name_en": "Samsung Galaxy S25 Ultra"},
    8: {"name": "Google Pixel 9 Pro", "name_ru": "Google Pixel 9 Pro", "name_en": "Google Pixel 9 Pro"},
    9: {"name": "Samsung Galaxy S25", "name_ru": "Samsung Galaxy S25", "name_en": "Samsung Galaxy S25"},
    10: {"name": "Тестовый телефон", "name_ru": "Тестовый телефон", "name_en": "Test Phone"},
    12: {"name": "Apple Watch Series 10", "name_ru": "Apple Watch Series 10", "name_en": "Apple Watch Series 10"},
    13: {"name": "Samsung Galaxy Watch 7", "name_ru": "Samsung Galaxy Watch 7", "name_en": "Samsung Galaxy Watch 7"},
}

print("Начало обновления базы данных...")

# Обновление Категорий
updated_categories = 0
for pk, data in categories_data.items():
    rows = Category.objects.filter(pk=pk).update(**data)
    updated_categories += rows

# Обновление Групп
updated_groups = 0
for pk, data in groups_data.items():
    rows = CharacteristicGroup.objects.filter(pk=pk).update(**data)
    updated_groups += rows

# Обновление Шаблонов
updated_templates = 0
for pk, data in templates_data.items():
    rows = CharacteristicTemplate.objects.filter(pk=pk).update(**data)
    updated_templates += rows

# Обновление Товаров
updated_products = 0
for pk, data in products_data.items():
    rows = Product.objects.filter(pk=pk).update(**data)
    updated_products += rows

print("Обновление завершено успешно!")
print(f"Категорий обновлено: {updated_categories}")
print(f"Групп характеристик обновлено: {updated_groups}")
print(f"Шаблонов характеристик обновлено: {updated_templates}")
print(f"Товаров обновлено: {updated_products}")