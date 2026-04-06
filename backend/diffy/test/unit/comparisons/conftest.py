"""Локальные фикстуры для unit-тестов comparisons."""
import pytest
from categories.models import Category
from products.models import Product
from comparisons.models import FavoriteComparison
from accounts.models import User


@pytest.fixture
def comparisons_category(db):
    """Тестовая категория для comparisons."""
    return Category.objects.create(
        name_ru='Электроника',
        name_en='Electronics'
    )


@pytest.fixture
def comparison_products(db, comparisons_category):
    """Создаёт 3 товара для сравнений."""
    products = [
        Product.objects.create(
            name_ru=f'Товар {i}',
            name_en=f'Product {i}',
            category=comparisons_category
        )
        for i in range(1, 4)
    ]
    return products


@pytest.fixture
def favorite_comparison(db, admin, comparison_products):
    """Создаёт избранное сравнение для админа."""
    comparison = FavoriteComparison.objects.create(
        user=admin,
        products_hash='1,2,3'
    )
    comparison.products.set(comparison_products)
    return comparison


@pytest.fixture
def user_favorite_comparison(db, user, comparison_products):
    """Создаёт избранное сравнение для обычного пользователя."""
    comparison = FavoriteComparison.objects.create(
        user=user,
        products_hash='1,2'
    )
    comparison.products.set(comparison_products[:2])
    return comparison
