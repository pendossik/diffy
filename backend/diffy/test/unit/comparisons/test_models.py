"""Тесты моделей приложения comparisons."""
import pytest
from django.contrib.auth import get_user_model
from comparisons.models import FavoriteComparison
from products.models import Category, Product

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestFavoriteComparisonStr:
    """Тесты строкового представления FavoriteComparison."""

    def test_str_returns_username_with_count(self):
        """__str__ возвращает username пользователя и количество товаров."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            username='comparison_user',
            is_active=True
        )
        comparison = FavoriteComparison.objects.create(user=user)

        result = str(comparison)

        assert "comparison_user" in result
        assert "set" in result

    def test_str_does_not_raise_error(self):
        """__str__ не вызывает AttributeError при доступе к user.username."""
        user = User.objects.create_user(
            email='test2@example.com',
            password='TestPass123!',
            username='test_user2',
            is_active=True
        )
        comparison = FavoriteComparison.objects.create(user=user)

        # Если баг CR-2 не исправлен, этот вызов упадёт с AttributeError
        result = str(comparison)

        assert result is not None
        assert isinstance(result, str)
