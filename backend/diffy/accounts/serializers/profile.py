from rest_framework import serializers
from accounts.models import User

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

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор вывода данных текущего пользователя."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChangeUsernameSerializer(serializers.Serializer):
    """Сериализатор для смены имени пользователя."""
    new_username = serializers.CharField(required=True)
    
    # Валидацию можно оставить здесь, так как она привязана к формату ввода
    def validate_new_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
        return value
