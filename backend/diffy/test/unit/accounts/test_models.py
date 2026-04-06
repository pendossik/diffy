"""Тесты модели User."""
import pytest
from accounts.models import User


pytestmark = pytest.mark.django_db


class TestUserStr:
    """Тесты строкового представления пользователя."""

    def test_str_returns_username(self):
        """__str__ возвращает username, а не email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            username='test_user',
            is_active=True
        )

        assert str(user) == 'test_user'

    def test_str_with_special_characters(self):
        """__str__ корректно обрабатывает специальные символы в username."""
        user = User.objects.create_user(
            email='test2@example.com',
            password='TestPass123!',
            username='user_123.test',
            is_active=True
        )

        assert str(user) == 'user_123.test'
