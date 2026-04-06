from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

# Для управления паролями
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError as DjangoValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # заблокирован до подтверждения почты
        )
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Попробуем аутентифицировать
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Неверный email или пароль")

        data = super().validate(attrs)
        data['user'] = {'id': self.user.id, 'email': self.user.email}
        return data
    

# --- СМЕНА ПАРОЛЯ ДЛЯ АВТОРИЗОВАННЫХ ---
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            validators.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

# --- СБРОС ПАРОЛЯ (ЗАПРОС НА ПОЧТУ) ---
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

# --- УСТАНОВКА НОВОГО ПАРОЛЯ (ПО ТОКЕНУ ИЗ ПОЧТЫ) ---
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            validators.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value
    
# --- СБРОС ЮЗЕРНЕЙМА ---
class ChangeUsernameSerializer(serializers.Serializer):
    """
    Сериализатор для смены имени пользователя.
    Не требует ввода пароля.
    """
    new_username = serializers.CharField(required=True)

    def validate_new_username(self, value):
        # Проверяем, что новый username не занят
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
        return value

class ActivationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(help_text="Закодированный ID пользователя")
    token = serializers.CharField(help_text="Токен активации")


class AdminForcePasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=False, 
        help_text="Новый пароль. Если оставить пустым, система сгенерирует случайный."
    )
