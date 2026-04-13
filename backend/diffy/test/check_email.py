# check_email.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Отправляем тестовое письмо на {settings.DEFAULT_FROM_EMAIL}...")

try:
    send_mail(
        subject='🔥 Тест реальной отправки',
        message='Если ты это читаешь, значит SMTP настроен верно!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['твой_реальный_email@gmail.com'],  # <--- ВПИШИ СЮДА СВОЙ EMAIL
        fail_silently=False,
    )
    print("✅ Письмо ушло! Проверь почту (и спам).")
except Exception as e:
    print(f"❌ Ошибка: {e}")