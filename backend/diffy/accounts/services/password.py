from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import logging

from accounts.models.user import User
from .email import EmailService

logger = logging.getLogger('accounts')

class PasswordService:
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValueError("Неверный текущий пароль.")
        user.set_password(new_password)
        user.save()
        logger.info(f"Пользователь {user.email} сменил пароль.")

    @staticmethod
    def request_password_reset(email: str) -> None:
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/password_reset/{uid}/{token}/"
            EmailService.send_password_reset_email(email=user.email, reset_link=reset_link)
        else:
            logger.warning(f"Запрос сброса пароля для несуществующего email: {email}")
            # Возвращаем None без ошибки (защита от перебора email)

    @staticmethod
    def confirm_password_reset(uidb64: str, token: str, new_password: str) -> None:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValueError("Ссылка недействительна или устарела.")

        if not default_token_generator.check_token(user, token):
            raise ValueError("Ссылка недействительна или устарела.")

        user.set_password(new_password)
        user.save()
        logger.info(f"Пароль для {user.email} успешно сброшен по токену.")