from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings

from rest_framework.exceptions import ValidationError


class UserService:
    @staticmethod
    @transaction.atomic
    def register_user(validated_data: dict) -> User:
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,  # заблокирован до подтверждения почты
        )
        UserService._send_activation_email(user)
        return user

    @staticmethod
    def _send_activation_email(user: User) -> None:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

        send_mail(
            'Подтверждение регистрации',
            f'Для активации: {activation_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def _get_user_from_uidb64(uidb64: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    @staticmethod
    def activate_account(uidb64: str, token: str) -> None:
        user = UserService._get_user_from_uidb64(uidb64)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return

        raise ValidationError({"error": "Неверный или просроченный токен"})

    @staticmethod
    def change_username(user: User, new_username: str) -> User:
        user.username = new_username
        user.save()
        return user

    @staticmethod
    def delete_account(user: User) -> None:
        user.delete()
