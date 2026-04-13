from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class LogoutRequestSerializer(serializers.Serializer):
    """Сериализатор для выхода пользователя."""
    refresh = serializers.CharField(
        help_text="JWT refresh-токен для добавления в чёрный список"
    )
    
    class Meta:
        ref_name = 'AccountLogout'

"""
    Для фронтенда при Логине помимо refresh и access токенов добавляем данные о пользователе
"""
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор логина.
    Проверяет email/пароль и добавляет данные юзера в ответ.
    """
    def validate(self, attrs):
        # Вызываем базовую валидацию (она сама проверит пароль и is_active)
        data = super().validate(attrs)
        
        # Добавляем нужные поля для фронтенда
        data['user'] = {
            'id': self.user.id, 
            'email': self.user.email,
            'role': self.user.role,
            'username': self.user.username
        }
        return data
    
class ActivationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(help_text="Закодированный ID пользователя")
    token = serializers.CharField(help_text="Токен активации")
