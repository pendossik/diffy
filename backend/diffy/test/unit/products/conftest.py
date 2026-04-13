"""Локальные фикстуры для тестов products views."""
import pytest
from products.models import Product
from categories.models import Category


@pytest.fixture
def cleanup_products():
    """
    Фикстура для очистки товаров после теста.

    Использование:
        def test_something(cleanup_products):
            # Тест создаёт товары
            # После теста все товары будут удалены
    """
    yield
    Product.objects.all().delete()


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
def test_category(cleanup_categories):
    """
    Создать одну тестовую категорию для товаров.

    Возвращает категорию.
    Автоматически очищается после теста.
    """
    return Category.objects.create(
        name_ru='Тестовая категория',
        name_en='Test Category'
    )


@pytest.fixture
def test_category2(cleanup_categories):
    """
    Создать вторую тестовую категорию для товаров.

    Возвращает категорию.
    Автоматически очищается после теста.
    """
    return Category.objects.create(
        name_ru='Вторая категория',
        name_en='Second Category'
    )


@pytest.fixture
def test_product(cleanup_products, test_category):
    """
    Создать один тестовый товар.

    Возвращает товар.
    Автоматически очищается после теста.
    """
    return Product.objects.create(
        name_ru='Тестовый товар',
        name_en='Test Product',
        category=test_category,
        img='products/test.jpg'
    )


@pytest.fixture
def many_products(cleanup_products, test_category):
    """
    Создать 25 товаров для тестирования пагинации.

    Возвращает список созданных товаров.
    Автоматически очищается после теста.
    """
    products_data = [
        (f'Товар {i:02d}', f'Product {i:02d}')
        for i in range(1, 26)
    ]

    products = [
        Product.objects.create(
            name_ru=ru,
            name_en=en,
            category=test_category,
            img=f'products/product-{i:02d}.jpg'
        )
        for i, (ru, en) in enumerate(products_data, 1)
    ]

    return products


@pytest.fixture
def searchable_products(cleanup_products, test_category):
    """
    Создать товары для тестирования поиска.

    Возвращает dict с товарами по ключам.
    Автоматически очищается после теста.
    """
    products = {
        'laptop': Product.objects.create(
            name_ru='Ноутбук Dell XPS 15',
            name_en='Dell XPS 15 Laptop',
            category=test_category,
            img='products/dell-xps-15.jpg'
        ),
        'phone': Product.objects.create(
            name_ru='Смартфон iPhone 15',
            name_en='iPhone 15 Smartphone',
            category=test_category,
            img='products/iphone-15.jpg'
        ),
        'tablet': Product.objects.create(
            name_ru='Планшет iPad Pro',
            name_en='iPad Pro Tablet',
            category=test_category,
            img='products/ipad-pro.jpg'
        ),
        'headphones': Product.objects.create(
            name_ru='Наушники Sony WH-1000XM5',
            name_en='Sony WH-1000XM5 Headphones',
            category=test_category,
            img='products/sony-headphones.jpg'
        ),
        'watch': Product.objects.create(
            name_ru='Умные часы Apple Watch',
            name_en='Apple Watch Smartwatch',
            category=test_category,
            img='products/apple-watch.jpg'
        ),
    }

    return products


@pytest.fixture
def products_in_different_categories(cleanup_products, test_category, test_category2):
    """
    Создать товары в разных категориях для тестирования фильтрации.

    Возвращает dict с товарами.
    Автоматически очищается после теста.
    """
    products = {
        'cat1_product1': Product.objects.create(
            name_ru='Товар 1 в категории 1',
            name_en='Product 1 in Category 1',
            category=test_category,
            img='products/cat1-product1.jpg'
        ),
        'cat1_product2': Product.objects.create(
            name_ru='Товар 2 в категории 1',
            name_en='Product 2 in Category 1',
            category=test_category,
            img='products/cat1-product2.jpg'
        ),
        'cat2_product1': Product.objects.create(
            name_ru='Товар 1 в категории 2',
            name_en='Product 1 in Category 2',
            category=test_category2,
            img='products/cat2-product1.jpg'
        ),
    }

    return products
