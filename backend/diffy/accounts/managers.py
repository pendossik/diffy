"""Менеджеры для кастомной модели пользователя."""
from django.contrib.auth.models import BaseUserManager
import logging

logger = logging.getLogger('accounts')


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.
    
    Обрабатывает создание обычных пользователей и суперпользователей 
    с корректным назначением ролей и логированием.
    """
    
    def create_user(self, email: str, password: str = None, **extra_fields):
        """
        Создать и вернуть обычного пользователя с указанными email и паролем.
        
        Аргументы:
            email: Email-адрес пользователя (будет нормализован)
            password: Пароль в открытом виде (будет захеширован)
            **extra_fields: Дополнительные поля для установки в пользователе
            
        Возвращает:
            User: Созданный экземпляр пользователя
            
        Исключения:
            ValueError: Если email не указан
        """
        if not email:
            raise ValueError('Пользователь должен иметь email-адрес')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        logger.info(f"Пользователь создан: {email}")
        return user
    
    def create_superuser(self, email: str, password: str = None, **extra_fields):
        """
        Создать и вернуть суперпользователя с правами администратора.
        
        Автоматически устанавливает is_staff=True, is_superuser=True, role='superuser'.
        
        Аргументы:
            email: Email суперпользователя
            password: Пароль в открытом виде
            **extra_fields: Дополнительные поля (переопределяются для суперюзера)
            
        Возвращает:
            User: Созданный экземпляр суперпользователя
            
        Исключения:
            ValueError: Если is_staff или is_superuser явно установлены в False
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superuser')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)