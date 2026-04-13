"""Модели приложения accounts."""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя с ролевой системой доступа.
    
    Роли:
        - user: Обычный авторизованный пользователь
        - admin: Сотрудник с доступом в админ-панель
        - superuser: Полный доступ ко всем функциям системы
    """
    
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
        ('superuser', 'Суперпользователь'),
    )
    
    email = models.EmailField(unique=True, verbose_name='Email')
    username = models.CharField(max_length=150, unique=True, verbose_name='Имя пользователя')
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user', 
        verbose_name='Роль'
    )
    is_active = models.BooleanField(default=False, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Статус сотрудника')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """
        Синхронизировать поле role с флагами прав Django перед сохранением.
        
        Обеспечивает согласованность между кастомной ролью 
        и встроенными флагами is_staff/is_superuser.
        """
        if self.role == 'superuser':
            self.is_superuser, self.is_staff = True, True
        elif self.role == 'admin':
            self.is_staff, self.is_superuser = True, False
        else:
            self.is_staff = self.is_superuser = False
        super().save(*args, **kwargs)