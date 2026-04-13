from rest_framework import serializers

class AdminForcePasswordResetSerializer(serializers.Serializer):
    """Сериализатор для принудительного сброса пароля администратором."""
    new_password = serializers.CharField(
        required=False, 
        help_text="Новый пароль. Если оставить пустым, система сгенерирует случайный."
    )