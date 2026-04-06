"""Локальные фикстуры для тестов categories views."""
import pytest
from categories.models import Category
from products.models import Product


@pytest.fixture
def cleanup_categories():
    """
    Фикстура для очистки категорий после теста.

    Сначала удаляет все товары (PROTECT не даёт удалить категорию с товарами),
    затем очищает категории.

    Использование:
        def test_something(cleanup_categories):
            # Тест создаёт категории
            # После теста все категории будут удалены
    """
    yield
    Product.objects.all().delete()
    Category.objects.all().delete()


@pytest.fixture
def many_categories(cleanup_categories):
    """
    Создать 25 категорий для тестирования пагинации.
    
    Возвращает список созданных категорий.
    Автоматически очищается после теста.
    """
    categories_data = [
        (f'Категория {i:02d}', f'Category {i:02d}')
        for i in range(1, 26)
    ]
    
    categories = [
        Category.objects.create(name_ru=ru, name_en=en)
        for ru, en in categories_data
    ]
    
    return categories


@pytest.fixture
def searchable_categories(cleanup_categories):
    """
    Создать категории для тестирования поиска.
    
    Возвращает dict с категориями по ключам.
    Автоматически очищается после теста.
    """
    categories = {
        'electronics': Category.objects.create(
            name_ru='Электроника',
            name_en='Electronics'
        ),
        'phones': Category.objects.create(
            name_ru='Телефоны',
            name_en='Phones'
        ),
        'laptops': Category.objects.create(
            name_ru='Ноутбуки',
            name_en='Laptops'
        ),
        'tablets': Category.objects.create(
            name_ru='Планшеты',
            name_en='Tablets'
        ),
        'clothing': Category.objects.create(
            name_ru='Одежда',
            name_en='Clothing'
        ),
    }
    
    return categories
