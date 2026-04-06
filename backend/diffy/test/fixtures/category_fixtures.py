"""Фикстуры для тестов приложения categories."""
import pytest
from categories.models import Category


@pytest.fixture
def category():
    """Создать одну категорию с переводами."""
    return Category.objects.create(
        name_ru='Тестовая категория',
        name_en='Test Category'
    )


@pytest.fixture
def categories_batch():
    """Создать пакет категорий для тестирования поиска и пагинации."""
    categories_data = [
        ('Электроника', 'Electronics'),
        ('Телефоны', 'Phones'),
        ('Ноутбуки', 'Laptops'),
        ('Планшеты', 'Tablets'),
        ('Аксессуары', 'Accessories'),
        ('Одежда', 'Clothing'),
        ('Обувь', 'Footwear'),
        ('Спорт', 'Sports'),
        ('Книги', 'Books'),
        ('Игры', 'Games'),
    ]
    return [
        Category.objects.create(name_ru=ru, name_en=en)
        for ru, en in categories_data
    ]


@pytest.fixture
def duplicate_category():
    """Создать категорию с именем, которое может вызвать конфликт."""
    return Category.objects.create(
        name_ru='Дубликат',
        name_en='Duplicate'
    )