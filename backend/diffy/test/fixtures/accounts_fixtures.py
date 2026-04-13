"""Фикстуры для тестов приложения accounts."""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# =============================================================================
# 🔧 Базовые фикстуры (НЕ меняют глобальный api_client!)
# =============================================================================

@pytest.fixture
def api_client():
    """API-клиент для тестов запросов (без авторизации)."""
    return APIClient()


@pytest.fixture
def user_factory():
    """Фабрика для создания пользователей."""
    def _create_user(email='test@example.com', password='TestPass123!', is_active=True, username=None, **kwargs):
        if username is None:
            username = email.split('@')[0]
        return User.objects.create_user(email=email, password=password, is_active=is_active, username=username, **kwargs)
    return _create_user

# =============================================================================
# 👥 Пользователи (только объекты, БЕЗ авторизации клиента!)
# =============================================================================
@pytest.fixture
def user(user_factory):
    """Обычный пользователь (роль 'user')."""
    return user_factory(
        email='user@test.com', 
        password='TestPass123!', 
        role='user',
        is_active=True  # ← КРИТИЧНО: для тестов пользователь должен быть активен
    )


@pytest.fixture
def admin(user_factory):
    """Администратор (роль 'admin')."""
    return user_factory(
        email='admin@test.com', 
        password='TestPass123!', 
        role='admin', 
        is_staff=True,
        is_active=True  # ← ДОБАВИТЬ
    )


@pytest.fixture
def superuser(user_factory):
    """Суперпользователь (роль 'superuser')."""
    return user_factory(
        email='super@test.com',
        password='TestPass123!',
        role='superuser',
        is_staff=True,
        is_superuser=True,
        is_active=True  # ← ДОБАВИТЬ
    )

@pytest.fixture
def active_user(user_factory):
    """Активный пользователь для тестов аутентификации."""
    # ← ВАЖНО: пароль должен совпадать с тем, что в тестах!
    return user_factory(email='active@test.com', password='TestPass123!', is_active=True)


@pytest.fixture
def inactive_user(user_factory):
    """Неактивный пользователь (после регистрации)."""
    return user_factory(email='inactive@test.com', password='TestPass123!', is_active=False)


# =============================================================================
# 🔐 JWT-авторизованные клиенты (для категорий и других эндпоинтов)
# =============================================================================

@pytest.fixture
def jwt_user_client(user):
    """
    Клиент с авторизацией обычного пользователя через JWT.
    
    Создаёт изолированный APIClient с валидным токеном.
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    return client


@pytest.fixture
def jwt_admin_client(admin):
    """
    Клиент с авторизацией администратора через JWT.
    
    Создаёт изолированный APIClient с валидным токеном.
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(admin)
    
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    return client

# =============================================================================
# 🎭 Моки для внешних зависимостей
# =============================================================================

@pytest.fixture
def mock_send_mail():
    """Мок для отправки писем."""
    with patch('accounts.services.send_mail') as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_signer():
    """Мок для TimestampSigner."""
    with patch('accounts.services.signer') as mock:
        mock.sign.return_value = 'mocked_token_123'
        mock.unsign.return_value = 1
        yield mock


@pytest.fixture
def mock_validate_password():
    """Мок для валидации пароля."""
    with patch('accounts.services.validate_password') as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def auth_tokens(active_user):
    """Генерирует пару JWT-токенов для пользователя."""
    refresh = RefreshToken.for_user(active_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }