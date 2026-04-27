import pytest
from unittest.mock import MagicMock


@pytest.fixture
def regular_user():
    """Создаёт мок пользователя без прав администратора."""
    user = MagicMock()
    user.is_authenticated = True
    user.role = None
    user.is_staff = False
    user.is_superuser = False
    return user


@pytest.fixture
def anonymous_user():
    """Создаёт мок анонимного пользователя."""
    user = MagicMock()
    user.is_authenticated = False
    return user


@pytest.fixture
def admin_user():
    """Создаёт мок пользователя с правами администратора."""
    user = MagicMock()
    user.is_authenticated = True
    user.role = 'admin'
    user.is_staff = False
    user.is_superuser = False
    return user