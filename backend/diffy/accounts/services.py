"""Бизнес-логика приложения accounts."""
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
import logging
from .models import User

logger = logging.getLogger('accounts')


class AuthService:
    """
    Сервисный класс для операций, связанных с аутентификацией.
    
    Все методы статические; там, где происходит изменение данных, 
    используется транзакционность. Обрабатывает регистрацию, 
    активацию, вход, выход и получение профиля.
    """
    
    @staticmethod
    @transaction.atomic
    def register_user(email: str, password: str, username: str) -> User:
        """
        Зарегистрировать нового пользователя по email, username и паролю.

        Создаёт неактивный аккаунт и отправляет письмо с активацией.
        Транзакция обеспечивает атомарность: если письмо не удалось отправить —
        пользователь НЕ создаётся (откат).

        Аргументы:
            email: Email-адрес пользователя
            password: Пароль в открытом виде
            username: Имя пользователя для отображения

        Возвращает:
            User: Созданный экземпляр пользователя (неактивный)

        Исключения:
            ValueError: Если email уже зарегистрирован
            Exception: Если не удалось отправить письмо (транзакция откатывается)
        """
        if User.objects.filter(email=email).exists():
            logger.warning(f"Регистрация не удалась: Email {email} уже зарегистрирован.")
            raise ValueError("Email уже зарегистрирован")

        if User.objects.filter(username=username).exists():
            logger.warning(f"Регистрация не удалась: Username {username} уже занят.")
            raise ValueError("Username уже занят")

        try:
            validate_password(password, user=None)
        except ValidationError as e:
            logger.warning(f"Регистрация: слабый пароль для {email}")
            raise ValueError("Пароль не соответствует требованиям безопасности")

        user = User.objects.create_user(email=email, password=password, username=username, is_active=False)
        # Генерируем токен через default_token_generator — не раскрывает ID пользователя
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f'{settings.BACKEND_URL}/api/accounts/activate/{uid}/{token}/'

        try:
            send_mail(
                subject='Активация аккаунта',
                message=f'Перейдите для активации: {activation_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(
                f"Не удалось отправить письмо на {email}. "
                f"Регистрация отменена, пользователь не создан."
            )
            raise ValueError(
                "Не удалось завершить регистрацию. Попробуйте позже."
            )

        logger.info(f"Письмо с активацией отправлено на {email}")

        return user
    
    @staticmethod
    @transaction.atomic
    def activate_account(uid: str, token: str) -> User:
        """
        Активировать аккаунт пользователя по токену из письма.

        Токен действует 24 часа. Активация идемпотентна.

        Аргументы:
            uid: URL-safe base64-encoded ID пользователя
            token: Токен активации от default_token_generator

        Возвращает:
            User: Активированный экземпляр пользователя

        Исключения:
            ValueError: Если токен невалиден, истёк или пользователь не найден
        """
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            logger.warning("Активация не удалась: пользователь не найден по токену.")
            raise ValueError("Невалидный токен активации")

        if not default_token_generator.check_token(user, token):
            logger.warning(
                f"Активация не удалась: невалидный или истёкший токен для пользователя {user.email}."
            )
            raise ValueError("Невалидный или истёкший токен активации")

        if user.is_active:
            logger.info(f"Пользователь {user.email} уже активен.")
            return user

        user.is_active = True
        user.save()
        logger.info(f"Пользователь {user.email} активирован.")
        return user
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Аутентифицировать пользователя и вернуть JWT-токены.
        
        Проверяет учётные данные, статус аккаунта, генерирует пару токенов.
        
        Аргументы:
            email: Email пользователя
            password: Пароль в открытом виде
            
        Возвращает:
            dict: {'refresh': str, 'access': str, 'user': User}
            
        Исключения:
            ValueError: Если учётные данные невалидны или аккаунт не активен
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Вход не удался: пользователь {email} не найден.")
            raise ValueError("Неверные учётные данные")
        
        if not user.check_password(password):
            logger.warning(f"Вход не удался: неверный пароль для {email}.")
            raise ValueError("Неверные учётные данные")
        
        if not user.is_active:
            logger.warning(f"Вход не удался: аккаунт {email} не активен.")
            raise ValueError("Аккаунт не активирован")
        
        refresh = RefreshToken.for_user(user)
        logger.info(f"Пользователь {email} успешно вошёл в систему.")
        
        return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user_id': user.id,
        'email': user.email,
        'role': user.role
        }
    
    @staticmethod
    @transaction.atomic
    def logout_user(refresh_token: str) -> bool:
        """
        Добавить refresh-токен в чёрный список для завершения сессии.
        
        Требует установленное приложение token_blacklist. Операция идемпотентна.
        
        Аргументы:
            refresh_token: JWT refresh-токен для добавления в чёрный список
            
        Возвращает:
            bool: True если токен добавлен в чёрный список, False если не найден
        
        Исключения:
            ValueError: Если произошла ошибка при добавлении в блэклист.
        """
        try:
            token = OutstandingToken.objects.get(token=refresh_token)
            BlacklistedToken.objects.get_or_create(token=token)
            logger.info(f"Токен добавлен в чёрный список для выхода.")
            return True
        except OutstandingToken.DoesNotExist:
            logger.warning("Выход: токен не найден в списке активных.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении токена в блэклист: {str(e)}")
            raise ValueError("Не удалось завершить сессию")
        
    @staticmethod
    def get_user_profile(user: User) -> dict:
        """
        Получить данные профиля пользователя для отображения.
        
        Аргументы:
            user: Аутентифицированный экземпляр User
            
        Возвращает:
            dict: Сериализованная информация профиля
        """
        return {
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined
        }