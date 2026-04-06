"""Сериализаторы приложения accounts."""
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации пользователя.

    Принимает email, username и пароль, возвращает сообщение о подтверждении.
    Пароль доступен только для записи и проверяется на минимальную длину.
    """
    email = serializers.EmailField(
        help_text="Email-адрес пользователя для регистрации и входа"
    )
    username = serializers.CharField(
        max_length=150,
        help_text="Имя пользователя для отображения в системе"
    )
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Пароль должен содержать не менее 8 символов"
    )
    
    class Meta:
        ref_name = 'AccountRegister'


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя.
    
    Проверяет учётные данные и возвращает JWT-токены при успехе.
    """
    email = serializers.EmailField(help_text="Зарегистрированный email пользователя")
    password = serializers.CharField(write_only=True, help_text="Пароль пользователя")
    
    class Meta:
        ref_name = 'AccountLogin'


class ActivateSerializer(serializers.Serializer):
    """
    Сериализатор для токена активации аккаунта.
    
    Проверяет подписанный токен, полученный по почте.
    """
    token = serializers.CharField(
        help_text="Токен активации, полученный по электронной почте",
        write_only=True
    )
    
    class Meta:
        ref_name = 'AccountActivate'


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных профиля пользователя.
    
    Представление информации о пользователе только для чтения.
    """
    class Meta:
        model = User
        fields = ('email', 'role', 'is_active', 'date_joined')
        read_only_fields = fields
        ref_name = 'UserProfile'

class LogoutRequestSerializer(serializers.Serializer):
    """Сериализатор для выхода пользователя."""
    refresh = serializers.CharField(
        help_text="JWT refresh-токен для добавления в чёрный список"
    )
    
    class Meta:
        ref_name = 'AccountLogout'