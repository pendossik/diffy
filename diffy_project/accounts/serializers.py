from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_date):
        user = User.objects.create_user(
            username=validated_date['username'],
            email=validated_date['email'],
            password=validated_date['password']
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
