from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return value


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
