# accounts/management/commands/create_super_user.py
"""Кастомные команды управления для приложения accounts."""
import getpass
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import logging
from accounts.models import User

logger = logging.getLogger('accounts')


class Command(BaseCommand):
    """
    Команда для создания суперпользователя с ролью 'superuser'.
    
    Использование:
        python manage.py create_super_user
    
    Интерактивно запрашивает email и пароль, проверяет ввод,
    создаёт пользователя с полными правами доступа.
    """
    
    help = 'Создание суперпользователя с ролью superuser'
    
    def add_arguments(self, parser):
        """
        Добавить аргументы командной строки для неинтерактивного режима.
        
        Позволяет создавать суперпользователя в скриптах и CI/CD:
            python manage.py create_super_user --email=admin@example.com --password=secret
        """
        parser.add_argument(
            '--email',
            type=str,
            help='Email суперпользователя (для неинтерактивного режима)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль суперпользователя (для неинтерактивного режима)'
        )
    
    def _validate_email(self, email: str) -> str:
        """
        Валидировать формат email-адреса.
        
        Аргументы:
            email: Строка с email для проверки
            
        Возвращает:
            str: Нормализованный email
            
        Исключения:
            CommandError: Если email невалиден
        """
        email = email.strip().lower()
        if not email or '@' not in email:
            raise CommandError('Некорректный формат email-адреса')
        return email
    
    def _validate_password(self, password: str) -> None:
        """
        Проверить сложность пароля.
        
        Требования:
            - Минимум 8 символов
            - Не должен быть слишком простым
            
        Аргументы:
            password: Пароль для проверки
            
        Исключения:
            CommandError: Если пароль не соответствует требованиям
        """
        if len(password) < 8:
            raise CommandError('Пароль должен содержать не менее 8 символов')
        
        # Простая проверка на слишком очевидные пароли
        weak_passwords = ['password', '12345678', 'qwerty123', 'admin123']
        if password.lower() in weak_passwords:
            raise CommandError('Пароль слишком простой, выберите более сложный')
    
    def _get_credentials_interactive(self) -> tuple[str, str]:
        """
        Запросить учётные данные в интерактивном режиме.
        
        Возвращает:
            tuple[str, str]: Кортеж (email, password)
        """
        # Запрос email с повтором при ошибке
        while True:
            email = input('Email суперпользователя: ').strip()
            try:
                email = self._validate_email(email)
                break
            except CommandError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))
                continue
        
        # Запрос пароля с подтверждением
        while True:
            password = getpass.getpass('Пароль: ')
            password_confirm = getpass.getpass('Подтвердите пароль: ')
            
            if password != password_confirm:
                self.stderr.write(self.style.ERROR('Пароли не совпадают'))
                continue
            
            try:
                self._validate_password(password)
                break
            except CommandError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))
                continue
        
        return email, password
    
    @transaction.atomic
    def _create_superuser(self, email: str, password: str) -> User:
        """
        Создать суперпользователя в базе данных.
        
        Атомарная операция: при ошибке все изменения откатываются.
        
        Аргументы:
            email: Email суперпользователя
            password: Пароль в открытом виде
            
        Возвращает:
            User: Созданный экземпляр суперпользователя
            
        Исключения:
            CommandError: Если пользователь уже существует или ошибка БД
        """
        if User.objects.filter(email=email).exists():
            logger.warning(f"Создание суперпользователя отклонено: {email} уже существует")
            raise CommandError(f'Пользователь с email "{email}" уже существует')
        
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                is_active=True  # Суперпользователь активен сразу
            )
            logger.info(f"Суперпользователь создан: {email}")
            return user
        except Exception as e:
            logger.error(f"Ошибка при создании суперпользователя {email}: {str(e)}")
            raise CommandError(f'Не удалось создать суперпользователя: {e}')
    
    def handle(self, *args, **options):
        """
        Точка входа команды.
        
        Определяет режим работы (интерактивный/неинтерактивный),
        валидирует ввод, создаёт суперпользователя и выводит результат.
        """
        email = options.get('email')
        password = options.get('password')
        
        # Определяем режим: неинтерактивный, если переданы аргументы
        if email and password:
            self.stdout.write(self.style.WARNING('Режим: неинтерактивный (аргументы CLI)'))
            try:
                email = self._validate_email(email)
                self._validate_password(password)
            except CommandError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка валидации: {e}'))
                return
        else:
            self.stdout.write(self.style.WARNING('Режим: интерактивный'))
            self.stdout.write('Нажмите Ctrl+C для отмены в любой момент\n')
            email, password = self._get_credentials_interactive()
        
        # Информационное предупреждение перед созданием
        self.stdout.write(f'\nБудет создан суперпользователь: {email}')
        self.stdout.write('Права: полный доступ ко всем функциям системы')
        
        if not options.get('email'):  # Только в интерактивном режиме спрашиваем подтверждение
            confirm = input('\nПродолжить? (да/нет): ').strip().lower()
            if confirm not in ('да', 'yes', 'y'):
                self.stdout.write(self.style.WARNING('Создание отменено пользователем'))
                return
        
        # Создание пользователя
        try:
            user = self._create_superuser(email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Суперпользователь "{user.email}" успешно создан!\n'
                    f'  ID: {user.id}\n'
                    f'  Роль: {user.role}\n'
                    f'  Активен: {user.is_active}'
                )
            )
        except CommandError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return