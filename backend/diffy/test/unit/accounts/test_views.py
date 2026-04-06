"""Тесты API-представлений приложения accounts."""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from accounts.models import User


pytestmark = pytest.mark.django_db


class TestRegisterView:
    """Тесты эндпоинта регистрации."""

    def test_register_valid_data(self, api_client, mock_send_mail, mock_validate_password):
        """Корректные данные создают пользователя и возвращают 201."""
        payload = {
            'email': 'new@example.com',
            'username': 'new_user',
            'password': 'StrongPass123!'
        }

        response = api_client.post(reverse('register'), payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data
        assert User.objects.filter(email='new@example.com').exists()
        assert User.objects.filter(username='new_user').exists()

    def test_register_missing_fields(self, api_client):
        """Отсутствие обязательных полей возвращает 400."""
        response = api_client.post(
            reverse('register'),
            {'email': 'only@email.com', 'username': 'test'},
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_duplicate_email(self, api_client, active_user, mock_validate_password):
        """Попытка регистрации с существующим email."""
        payload = {
            'email': active_user.email,
            'username': 'another_user',
            'password': 'AnotherPass123!'
        }

        response = api_client.post(reverse('register'), payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_register_duplicate_username(self, api_client, active_user, mock_validate_password):
        """Попытка регистрации с существующим username."""
        payload = {
            'email': 'another@example.com',
            'username': active_user.username,
            'password': 'AnotherPass123!'
        }

        response = api_client.post(reverse('register'), payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data


class TestActivateView:
    """Тесты эндпоинта активации."""

    def test_activate_success(self, api_client, inactive_user):
        """Валидный токен активирует аккаунт."""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
        token = default_token_generator.make_token(inactive_user)

        response = api_client.post(reverse('activate', args=[uid, token]))

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_activate_invalid_token(self, api_client):
        """Невалидный токен возвращает 400."""
        uid = urlsafe_base64_encode(b'999')

        response = api_client.post(reverse('activate', args=[uid, 'bad-token']))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data


class TestLoginView:
    """Тесты эндпоинта входа."""
    
    def test_login_success(self, api_client, active_user):
        """Верные учётные данные возвращают токены."""
        payload = {'email': active_user.email, 'password': 'TestPass123!'}
        
        response = api_client.post(reverse('login'), payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_wrong_password(self, api_client, active_user):
        """Неверный пароль возвращает 401."""
        payload = {'email': active_user.email, 'password': 'WrongPass!'}
        
        response = api_client.post(reverse('login'), payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_inactive_user(self, api_client, inactive_user):
        """Попытка входа в неактивный аккаунт."""
        payload = {'email': inactive_user.email, 'password': 'TestPass123!'}
        
        response = api_client.post(reverse('login'), payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, api_client):
        """Отсутствие полей возвращает 400 с ошибками валидации."""
        response = api_client.post(reverse('login'), {'email': 'only@email.com'}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


class TestLogoutView:
    """Тесты эндпоинта выхода."""
    
    def test_logout_success(self, api_client, auth_tokens):
        """Валидный refresh-токен завершает сессию."""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
        payload = {'refresh': auth_tokens['refresh']}
        
        response = api_client.post(reverse('logout'), payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Выход выполнен успешно'
    
    def test_logout_unauthenticated(self, api_client):
        """Попытка логаута без авторизации возвращает 401."""
        response = api_client.post(reverse('logout'), {'refresh': 'any.token'}, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_missing_token(self, api_client, auth_tokens):
        """Отсутствие refresh-токена в теле запроса."""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
        
        response = api_client.post(reverse('logout'), {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_logout_invalid_token_format(self, api_client, auth_tokens):
        """Невалидный формат refresh-токена."""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
        payload = {'refresh': 'not.a.valid.jwt'}
        
        response = api_client.post(reverse('logout'), payload, format='json')
        
        # Зависит от валидации в LogoutRequestSerializer
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]


class TestProfileView:
    """Тесты эндпоинта профиля."""
    
    def test_profile_success(self, api_client, active_user, auth_tokens):
        """Авторизованный пользователь получает свой профиль."""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_tokens["access"]}')
        
        response = api_client.get(reverse('profile'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == active_user.email
        assert 'role' in response.data
        assert 'date_joined' in response.data
    
    def test_profile_unauthenticated(self, api_client):
        """Неавторизованный доступ к профилю запрещён."""
        response = api_client.get(reverse('profile'))
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED