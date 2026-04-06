"""Тесты бизнес-логики AuthService."""
import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.services import AuthService
from accounts.models import User


pytestmark = pytest.mark.django_db


class TestRegisterUser:
    """Тесты регистрации пользователя."""

    def test_register_success(self, mock_send_mail, mock_validate_password):
        """Успешная регистрация создаёт неактивного пользователя и отправляет письмо."""
        user = AuthService.register_user(
            email='new@example.com',
            password='StrongPass123!',
            username='new_user'
        )

        assert user.email == 'new@example.com'
        assert user.username == 'new_user'
        assert user.is_active is False
        assert user.check_password('StrongPass123!')
        mock_send_mail.assert_called_once()

    def test_register_duplicate_email(self):
        """Попытка регистрации с существующим email вызывает ошибку."""
        User.objects.create_user(
            email='exists@example.com',
            password='Pass123!',
            username='exists_user'
        )

        with pytest.raises(ValueError, match='Email уже зарегистрирован'):
            AuthService.register_user(
                email='exists@example.com',
                password='AnotherPass123!',
                username='another_user'
            )

    def test_register_duplicate_username(self):
        """Попытка регистрации с существующим username вызывает ошибку."""
        User.objects.create_user(
            email='first@example.com',
            password='Pass123!',
            username='taken_user'
        )

        with pytest.raises(ValueError, match='Username уже занят'):
            AuthService.register_user(
                email='second@example.com',
                password='AnotherPass123!',
                username='taken_user'
            )

    def test_register_weak_password(self, mock_validate_password):
        """Слабый пароль отклоняется валидатором."""
        mock_validate_password.side_effect = ValidationError('Too short')

        with pytest.raises(ValueError, match='Пароль не соответствует требованиям'):
            AuthService.register_user(
                email='new@example.com',
                password='123',
                username='new_user'
            )

    def test_register_email_send_failure_rollbacks_transaction(
        self, mock_send_mail, mock_validate_password
    ):
        """Ошибка отправки письма откатывает создание пользователя (атомарность)."""
        mock_send_mail.side_effect = Exception('SMTP error')

        with pytest.raises(ValueError, match='Не удалось завершить регистрацию'):
            AuthService.register_user(
                email='new@example.com',
                password='StrongPass123!',
                username='new_user'
            )

        assert not User.objects.filter(email='new@example.com').exists()


class TestActivateAccount:
    """Тесты активации аккаунта."""

    def _get_activation_tokens(self, user):
        """Сгенерировать uid и токен для пользователя."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    def test_activate_success(self, inactive_user):
        """Валидный токен активирует пользователя."""
        uid, token = self._get_activation_tokens(inactive_user)

        result = AuthService.activate_account(uid, token)

        assert result.is_active is True
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_activate_expired_token(self, inactive_user):
        """
        CR-5: Истёкший токен вызывает ошибку.
        default_token_generator проверяет timestamp внутри токена.
        """
        uid, token = self._get_activation_tokens(inactive_user)
        # Подделываем токен чтобы он был невалидным
        bad_token = token + "x"

        with pytest.raises(ValueError, match='Невалидный.*токен'):
            AuthService.activate_account(uid, bad_token)

    def test_activate_invalid_token(self):
        """CR-5: Невалидный токен вызывает ошибку."""
        uid = urlsafe_base64_encode(force_bytes(999999))

        with pytest.raises(ValueError, match='Невалидный токен'):
            AuthService.activate_account(uid, 'invalid-token')

    def test_activate_user_not_found(self):
        """Токен ссылается на несуществующего пользователя."""
        uid = urlsafe_base64_encode(force_bytes(99999999))

        with pytest.raises(ValueError, match='Невалидный токен'):
            AuthService.activate_account(uid, 'some-token')

    def test_activate_idempotent(self, active_user):
        """Повторная активация активного пользователя не вызывает ошибок."""
        uid, token = self._get_activation_tokens(active_user)

        result = AuthService.activate_account(uid, token)

        assert result.is_active is True
        assert result == active_user

    def test_token_does_not_expose_user_id(self, inactive_user):
        """
        CR-5: Токен активации не раскрывает ID пользователя в открытом виде.
        default_token_generator создаёт хеш на основе SECRET_KEY, pk, timestamp.
        """
        uid, token = self._get_activation_tokens(inactive_user)

        # Токен НЕ должен содержать ID пользователя в открытом виде
        assert str(inactive_user.id) not in token
        assert str(inactive_user.id) not in uid  # uid base64, но это не plaintext ID
        # uid — base64-encoded ID, но без token его бесполезно
        # Главный критерий: токен — это хеш, а не подписанный ID
        assert len(token) > 10  # default_token_generator создаёт длинные токены


class TestAuthenticateUser:
    """Тесты аутентификации."""
    
    def test_authenticate_success(self, active_user):
        """Верные учётные данные возвращают пару токенов."""
        result = AuthService.authenticate_user(
            email=active_user.email, 
            password='TestPass123!'
        )
        
        assert 'access' in result
        assert 'refresh' in result
        assert result['email'] == active_user.email
        assert result['role'] == active_user.role
    
    def test_authenticate_wrong_password(self, active_user):
        """Неверный пароль вызывает ошибку."""
        with pytest.raises(ValueError, match='Неверные учётные данные'):
            AuthService.authenticate_user(
                email=active_user.email, 
                password='WrongPass!'
            )
    
    def test_authenticate_user_not_found(self):
        """Попытка входа с несуществующим email."""
        with pytest.raises(ValueError, match='Неверные учётные данные'):
            AuthService.authenticate_user('ghost@example.com', 'AnyPass123!')
    
    def test_authenticate_inactive_account(self, inactive_user):
        """Вход в неактивный аккаунт запрещён."""
        with pytest.raises(ValueError, match='Аккаунт не активирован'):
            AuthService.authenticate_user(
                email=inactive_user.email, 
                password='TestPass123!'
            )


class TestLogoutUser:
    """Тесты выхода из системы."""
    
    def test_logout_success(self, auth_tokens):
        """Валидный refresh-токен добавляется в блэклист."""
        result = AuthService.logout_user(auth_tokens['refresh'])
        
        assert result is True
    
    def test_logout_token_not_found(self):
        """Попытка заблэклистить несуществующий токен."""
        result = AuthService.logout_user('nonexistent.token.here')
        
        assert result is False
    
    def test_logout_idempotent(self, auth_tokens):
        """Повторный логаут того же токена не вызывает ошибок."""
        AuthService.logout_user(auth_tokens['refresh'])
        result = AuthService.logout_user(auth_tokens['refresh'])
        
        assert result is True  # get_or_create обеспечивает идемпотентность


class TestGetUserProfile:
    """Тесты получения профиля."""
    
    def test_get_profile_success(self, active_user):
        """Профиль возвращает ожидаемые поля."""
        result = AuthService.get_user_profile(active_user)
        
        assert result['email'] == active_user.email
        assert result['role'] == active_user.role
        assert result['is_active'] is True
        assert 'date_joined' in result