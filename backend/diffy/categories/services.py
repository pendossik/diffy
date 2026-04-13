"""Бизнес-логика приложения categories."""
from django.db import transaction
from django.db.models import QuerySet
import logging
from django.db.models import Q
from .models import Category
from accounts.models import User  # Импорт твоей кастомной модели

logger = logging.getLogger('categories')


class CategoryService:
    """
    Сервисный класс для операций с категориями.
    
    Все методы статические; операции записи — транзакционные.
    """
    
    @staticmethod
    def _is_admin(user: User) -> bool:
        """
        Проверка прав администратора.

        Работает как с кастомной ролью, так и со стандартными флагами Django.
        """
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, 'role', None) in ('admin', 'superuser') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )
        
    @staticmethod
    def get_categories_list(search: str = None) -> QuerySet:
        """
        Получить отсортированный список категорий с опциональным поиском.
        
        Аргументы:
            search: Поисковая подстрока (фильтрация по name__icontains)
            
        Возвращает:
            QuerySet: Категории, отсортированные по имени
        """
        queryset = Category.objects.all()
        if search and search.strip():
            search_term = search.strip()
            # Ищем совпадения в любом из языковых полей
            queryset = queryset.filter(
                Q(name_ru__icontains=search_term) | 
                Q(name_en__icontains=search_term)
            )
        return queryset.order_by('name')
    
    @staticmethod
    def get_category_detail(category_id: int) -> Category:
        """
        Получить категорию по ID.
        
        Аргументы:
            category_id: Первичный ключ категории
            
        Возвращает:
            Category: Экземпляр категории
            
        Исключения:
            ValueError: Если категория не найдена
        """
        try:
            return Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError("Категория не найдена")
    
    @staticmethod
    @transaction.atomic
    def create_category(user: User, name: str) -> Category:
        """
        Создать новую категорию.

        Аргументы:
            user: Пользователь, выполняющий операцию
            name: Название категории

        Возвращает:
            Category: Созданная категория

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если категория с таким именем уже существует или имя некорректно
        """
        if not CategoryService._is_admin(user):
            raise PermissionError("Только администраторы могут создавать категории")

        name = name.strip().capitalize()

        # Валидация длины имени (CRITICAL #3)
        if len(name) > 100:
            raise ValueError("Название категории не должно превышать 100 символов")

        if not name:
            raise ValueError("Название категории не может быть пустым")

        # Атомарная проверка и создание для предотвращения race condition (CRITICAL #2)
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            # Блокировка на уровне БД для предотвращения гонки
            if Category.objects.select_for_update().filter(name__iexact=name).exists():
                raise ValueError("Категория с таким именем уже существует")

            category = Category.objects.create(name=name)
            logger.info(f"Категория создана: '{name}' (пользователь: {user.email})")
            return category
    
    @staticmethod
    @transaction.atomic
    def update_category(user: User, category_id: int, name: str) -> Category:
        """
        Обновить название категории.

        Аргументы:
            user: Пользователь, выполняющий операцию
            category_id: ID категории
            name: Новое название

        Возвращает:
            Category: Обновлённая категория

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если категория не найдена или имя занято
        """
        if not CategoryService._is_admin(user):
            raise PermissionError("Только администраторы могут изменять категории")

        category = CategoryService.get_category_detail(category_id)
        name = name.strip().capitalize()

        # Валидация длины имени (CRITICAL #3)
        if len(name) > 100:
            raise ValueError("Название категории не должно превышать 100 символов")

        if not name:
            raise ValueError("Название категории не может быть пустым")

        # Атомарная проверка для предотвращения race condition (CRITICAL #2)
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            if Category.objects.select_for_update().filter(name__iexact=name).exclude(pk=category_id).exists():
                raise ValueError("Категория с таким именем уже существует")

            category.name = name
            category.save()
            logger.info(f"Категория обновлена: {category_id} -> '{name}' (пользователь: {user.email})")
            return category
    
    @staticmethod
    @transaction.atomic
    def delete_category(user: User, category_id: int) -> bool:
        """
        Удалить категорию.

        Запрещает удаление если в категории есть продукты или группы характеристик.

        Аргументы:
            user: Пользователь, выполняющий операцию
            category_id: ID категории

        Возвращает:
            bool: True если удаление успешно

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если категория не найдена или содержит продукты/группы характеристик
        """
        if not CategoryService._is_admin(user):
            raise PermissionError("Только администраторы могут удалять категории")

        category = CategoryService.get_category_detail(category_id)

        # Проверка на наличие продуктов
        product_count = category.products.count()
        if product_count > 0:
            logger.warning(
                f"Попытка удалить категорию с продуктами: "
                f"'{category.name}' (ID={category_id}), продуктов: {product_count}, "
                f"пользователь: {user.email}"
            )
            raise ValueError(
                f"Невозможно удалить категорию '{category.name}': "
                f"в ней содержится {product_count} товар(ов). "
                f"Сначала удалите или переместите товары."
            )

        # Проверка на наличие групп характеристик
        group_count = category.char_groups.count()
        if group_count > 0:
            logger.warning(
                f"Попытка удалить категорию с группами характеристик: "
                f"'{category.name}' (ID={category_id}), групп: {group_count}, "
                f"пользователь: {user.email}"
            )
            raise ValueError(
                f"Невозможно удалить категорию '{category.name}': "
                f"в ней содержится {group_count} групп(а) характеристик. "
                f"Сначала удалите группы характеристик."
            )

        category_name = category.name
        category.delete()
        logger.info(f"Категория удалена: '{category_name}' (пользователь: {user.email})")
        return True