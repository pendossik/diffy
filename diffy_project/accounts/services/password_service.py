from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied


class PasswordService:
    @staticmethod
    def _get_user_from_uidb64(uidb64: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValidationError({"old_password": ["Неверный текущий пароль."]})

        user.set_password(new_password)
        user.save()

    @staticmethod
    def request_password_reset(email: str) -> None:
        user = User.objects.filter(email=email).first()

        if not user:
            return

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/password_reset/{uid}/{token}/"

        send_mail(
            'Сброс пароля',
            f'Вы запросили сброс пароля. Для установки нового пароля перейдите по ссылке: {reset_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def confirm_password_reset(uidb64: str, token: str, new_password: str) -> None:
        user = PasswordService._get_user_from_uidb64(uidb64)

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return

        raise ValidationError({"error": "Ссылка недействительна или устарела."})

    @staticmethod
    def admin_force_password_reset(user_id: int, admin_user: User, new_password: str | None = None) -> dict:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound({"error": "Пользователь не найден."})

        if target_user.is_superuser and not admin_user.is_superuser:
            raise PermissionDenied({"error": "У вас нет прав менять пароль суперпользователю."})

        if not new_password:
            new_password = get_random_string(length=12)

        target_user.set_password(new_password)
        target_user.save()

        return {
            "message": f"Пароль для {target_user.email} успешно изменен.",
            "new_password": new_password,
        }
