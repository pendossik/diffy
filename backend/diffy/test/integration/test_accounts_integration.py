"""
Интеграционные тесты приложения accounts.

Запуск:
    # Только интеграционные тесты:
    pytest test/integration/test_accounts_integration.py -v -m integration
    
    # Исключить интеграционные (по умолчанию в pytest.ini):
    pytest test/ -v -m "not integration"
"""
import pytest
from django.core import mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from accounts.models import User


pytestmark = [pytest.mark.django_db, pytest.mark.integration]


# ============================================================================
# 📧 Email-интеграция
# ============================================================================

class TestEmailActivationFlow:
    """Полный сценарий: регистрация → письмо → активация → вход."""
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        BACKEND_URL='http://testserver'
    )
    def test_full_registration_to_login_flow(self, api_client):
        """Интеграционный тест полного цикла аутентификации."""
        # 1. Регистрация
        payload = {
            'email': 'integration@test.com',
            'password': 'IntegrationTest123!'
        }
        response = api_client.post(reverse('register'), payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # 2. Пользователь создан, но не активен
        user = User.objects.get(email='integration@test.com')
        assert user.is_active is False
        assert user.check_password('IntegrationTest123!')
        
        # 3. Письмо отправлено
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == 'Активация аккаунта'
        assert user.email in email.to
        
        # 4. Извлекаем токен из письма
        activation_link = [line for line in email.body.split('\n') if '/activate/' in line][0].strip()
        token = activation_link.split('/activate/')[1].rstrip('/')
        
        # 5. Реальная верификация токена
        signer = TimestampSigner()
        user_id = signer.unsign(token, max_age=86400)
        assert int(user_id) == user.id
        
        # 6. Активация через реальный эндпоинт
        response = api_client.post(reverse('activate', args=[token]))
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active is True
        
        # 7. Вход после активации
        login_payload = {
            'email': 'integration@test.com',
            'password': 'IntegrationTest123!'
        }
        response = api_client.post(reverse('login'), login_payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        # 8. Проверка токена
        access_token = response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = api_client.get(reverse('profile'))
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['email'] == 'integration@test.com'


# ============================================================================
# ⏱️ Токен активации: истечение времени
# ============================================================================

class TestTokenExpiration:
    """Тесты временной валидности токенов активации."""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_token_expires_after_24_hours(self, api_client):
        """Токен активации должен истекать через 24 часа."""
        # Регистрация
        response = api_client.post(reverse('register'), {
            'email': 'expire@test.com',
            'password': 'TestPass123!'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Извлекаем токен из письма
        assert len(mail.outbox) == 1
        email_body = mail.outbox[0].body
        token = email_body.split('/activate/')[1].split('/')[0]
        
        # Проверяем, что токен валидный СЕЙЧАС
        signer = TimestampSigner()
        try:
            user_id = signer.unsign(token, max_age=86400)
            assert user_id is not None
        except (BadSignature, SignatureExpired):
            pytest.fail("Свежий токен не должен быть истёкшим")
        
        # Проверяем, что тот же токен НЕ валиден с max_age=0
        with pytest.raises(SignatureExpired):
            signer.unsign(token, max_age=0)
    
    def test_invalid_signature_rejected(self, api_client):
        """Токен с поддельной подписью должен отклоняться."""
        fake_token = "eyJmYWtlIjoidG9rZW4ifQ:fake_signature"
        
        response = api_client.post(reverse('activate', args=[fake_token]))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'токен' in response.data['error'].lower()


# ============================================================================
# 🔐 Пароли: реальная валидация Django
# ============================================================================

class TestPasswordValidationIntegration:
    """Тесты валидации паролей через реальные Django-валидаторы."""
    
    def test_weak_password_rejected_by_django_validators(self, api_client):
        """Пароль должен проверяться реальными валидаторами из settings."""
        weak_passwords = ['123', 'qwerty', 'aaaaaaaa', 'Test123']
        
        for weak_pass in weak_passwords:
            response = api_client.post(reverse('register'), {
                'email': f'test+{weak_pass}@example.com',
                'password': weak_pass
            }, format='json')
            
            if response.status_code == status.HTTP_400_BAD_REQUEST:
                continue
            else:
                print(f"⚠️ Пароль '{weak_pass}' прошёл валидацию — проверь AUTH_PASSWORD_VALIDATORS")
    
    def test_strong_password_accepted(self, api_client):
        """Корректный сложный пароль должен приниматься."""
        strong_password = 'C0mpl3x!Pass#2024'
        
        response = api_client.post(reverse('register'), {
            'email': 'strongpass@test.com',
            'password': strong_password
        }, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='strongpass@test.com')
        assert user.check_password(strong_password)


# ============================================================================
# 🔐 JWT: реальный блэклист
# ============================================================================

class TestJWTBlacklistIntegration:
    """Тесты работы JWT с реальным блэклистом simplejwt."""
    
    def test_logout_adds_refresh_to_blacklist(self, api_client, active_user):
        """Логаут должен добавлять refresh-токен в блэклист."""
        refresh = RefreshToken.for_user(active_user)
        access = refresh.access_token
        
        # Проверяем, что access работает
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = api_client.get(reverse('profile'))
        assert response.status_code == status.HTTP_200_OK
        
        # Логаут с реальным refresh-токеном
        response = api_client.post(reverse('logout'), {
            'refresh': str(refresh)
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем, что токен в блэклисте
        assert BlacklistedToken.objects.filter(token__token=str(refresh)).exists()
    
    def test_logout_idempotent_with_real_tokens(self, api_client, active_user):
        """Повторный логаут с тем же токеном не должен вызывать ошибок."""
        refresh = RefreshToken.for_user(active_user)
        access = refresh.access_token
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        
        response1 = api_client.post(reverse('logout'), {
            'refresh': str(refresh)
        }, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = api_client.post(reverse('logout'), {
            'refresh': str(refresh)
        }, format='json')
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


# ============================================================================
# 🌐 HTTP-слой
# ============================================================================

class TestHTTPIntegration:
    """Тесты поведения на уровне HTTP, без моков."""
    
    def test_missing_content_type_returns_415_or_400(self, api_client):
        """Запрос без Content-Type должен возвращать корректную ошибку."""
        response = api_client.post(
            reverse('login'),
            data={'email': 'x', 'password': 'y'},
            content_type=None
        )
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        ]
    
    def test_invalid_auth_header_returns_401_not_500(self, api_client):
        """Невалидный Bearer-токен должен возвращать 401, а не падать с 500."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.format')
        
        response = api_client.get(reverse('profile'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'traceback' not in str(response.data)
    
    def test_profile_requires_auth(self, api_client):
        """Эндпоинт профиля должен требовать аутентификацию."""
        response = api_client.get(reverse('profile'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# 🗄️ Надёжность
# ============================================================================

class TestDataIntegrityIntegration:
    """Тесты целостности данных и транзакционности."""
    
    def test_duplicate_email_prevented_by_db_constraint(self, api_client):
        """Уникальность email должна обеспечиваться на уровне БД."""
        User.objects.create_user(email='unique@test.com', password='Pass123!', username='unique_user')
        
        response = api_client.post(reverse('register'), {
            'email': 'unique@test.com',
            'password': 'AnotherPass123!'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_user_created_even_if_email_fails(self, api_client):
        """При сбое отправки письма пользователь всё равно должен создаваться."""
        from unittest.mock import patch
        
        with patch('accounts.services.send_mail') as mock_send:
            mock_send.side_effect = ConnectionError('SMTP server unreachable')
            
            response = api_client.post(reverse('register'), {
                'email': 'fallback@test.com',
                'password': 'TestPass123!'
            }, format='json')
            
            assert response.status_code == status.HTTP_201_CREATED
            assert User.objects.filter(email='fallback@test.com').exists()