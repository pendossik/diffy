from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('accounts')

class EmailService:
    @staticmethod
    def send_activation_email(email: str, activation_link: str) -> None:
        try:
            send_mail(
                subject='Подтверждение регистрации',
                message=f'Для активации: {activation_link}',
                from_email=settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Письмо с активацией отправлено на {email}")
        except Exception as e:
            logger.error(f"Ошибка отправки активации на {email}: {str(e)}")
            raise ValueError("Ошибка при отправке письма. Регистрация не завершена.")

    @staticmethod
    def send_password_reset_email(email: str, reset_link: str) -> None:
        try:
            send_mail(
                subject='Сброс пароля',
                message=f'Вы запросили сброс пароля. Для установки нового перейдите по ссылке: {reset_link}',
                from_email=settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Письмо сброса пароля отправлено на {email}")
        except Exception as e:
            logger.error(f"Ошибка отправки сброса пароля на {email}: {str(e)}")
            raise ValueError("Ошибка отправки письма.")