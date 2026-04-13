"""Бизнес-логика приложения products."""
from django.db import transaction
from django.db.models import QuerySet, Case, When
import logging
from django.db.models import Q
from .models import Product
from accounts.models import User  # Импорт твоей кастомной модели

logger = logging.getLogger('products')


class ProductService:
    """
    Сервисный класс для операций с товарами.

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
    def get_products_list(search: str = None, category_id: int = None) -> QuerySet:
        """
        Получить отсортированный список товаров с опциональным поиском и фильтром.

        Аргументы:
            search: Поисковая подстрока (фильтрация по name__icontains)
            category_id: ID категории для фильтрации

        Возвращает:
            QuerySet: Товары, отсортированные по категории и имени
        """
        queryset = Product.objects.select_related('category').all()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search and search.strip():
            search_term = search.strip()
            # Ищем совпадения в любом из языковых полей
            queryset = queryset.filter(
                Q(name_ru__icontains=search_term) |
                Q(name_en__icontains=search_term)
            )

        return queryset.order_by('category__name', 'name')
    
    @staticmethod
    def get_product_detail(product_id: int) -> Product:
        """
        Получить товар по ID.
        
        Аргументы:
            product_id: Первичный ключ товара
            
        Возвращает:
            Product: Экземпляр товара
            
        Исключения:
            ValueError: Если товар не найден
        """
        try:
            return Product.objects.select_related('category').get(pk=product_id)
        except Product.DoesNotExist:
            raise ValueError("Товар не найден")
    
    @staticmethod
    @transaction.atomic
    def create_product(
        user: User,
        name: str,
        category_id: int,
        img: str = None,
        name_ru: str = None,
        name_en: str = None
    ) -> Product:
        """
        Создать новый товар.

        Аргументы:
            user: Пользователь, выполняющий операцию
            name: Название товара (для текущей локали)
            category_id: ID категории
            img: Путь к изображению (опционально)
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)

        Возвращает:
            Product: Созданный товар

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если товар с таким именем уже существует в категории
        """
        if not ProductService._is_admin(user):
            raise PermissionError("Только администраторы могут создавать товары")

        name = name.strip()

        # Валидация длины имени (CRITICAL #3)
        if len(name) > 200:
            raise ValueError("Название товара не должно превышать 200 символов")

        # Валидация пустого имени (CRITICAL #4)
        if not name:
            raise ValueError("Название товара не может быть пустым")

        # Проверяем существование категории
        from categories.models import Category
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError("Категория не найдена")

        # Атомарная проверка и создание для предотвращения race condition (CRITICAL #2)
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            # Блокировка на уровне БД для предотвращения гонки
            if Product.objects.select_for_update().filter(
                category=category
            ).filter(
                Q(name_ru__iexact=name) | Q(name_en__iexact=name)
            ).exists():
                raise ValueError("Товар с таким именем уже существует в этой категории")

            # Если переводы не указаны — используем name
            if name_ru is None or name_ru == '':
                name_ru = name
            if name_en is None or name_en == '':
                name_en = name

            # Создаем объект с явным указанием всех переводов
            product = Product(
                category=category,
                img=img,
                name_ru=name_ru,
                name_en=name_en,
            )
            product.save()

            logger.info(f"Товар создан: '{name}' (пользователь: {user.email}) | "
                        f"RU: {name_ru} | EN: {name_en}")
            return product


    @staticmethod
    @transaction.atomic
    def update_product(
        user: User,
        product_id: int,
        name: str = None,
        category_id: int = None,
        img: str = None,
        name_ru: str = None,
        name_en: str = None
    ) -> Product:
        """
        Обновить товар.

        Аргументы:
            user: Пользователь, выполняющий операцию
            product_id: ID товара
            name: Новое название (опционально)
            category_id: Новый ID категории (опционально)
            img: Новый путь к изображению (опционально)
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)

        Возвращает:
            Product: Обновлённый товар

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если товар не найден или имя занято
        """
        if not ProductService._is_admin(user):
            raise PermissionError("Только администраторы могут изменять товары")

        product = ProductService.get_product_detail(product_id)

        # Валидация и обновление name
        if name is not None:
            name = name.strip()

            # Валидация пустого имени (CRITICAL #4) - ПЕРЕД проверкой уникальности
            if not name:
                raise ValueError("Название товара не может быть пустым")

            # Валидация длины имени (CRITICAL #3) - ПЕРЕД проверкой уникальности
            if len(name) > 200:
                raise ValueError("Название товара не должно превышать 200 символов")

            product.name = name

        # Обновляем переводы
        if name_ru is not None:
            name_ru = name_ru.strip() if name_ru else ''
            if name_ru == '':
                name_ru = name or product.name
            product.name_ru = name_ru

        if name_en is not None:
            name_en = name_en.strip() if name_en else ''
            if name_en == '':
                name_en = name or product.name
            product.name_en = name_en

        # Проверяем уникальность если изменилось имя
        check_name = name or product.name_ru
        check_category_id = category_id if category_id else product.category_id

        # Атомарная проверка для предотвращения race condition (CRITICAL #2)
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            if Product.objects.select_for_update().filter(
                category_id=check_category_id
            ).filter(
                Q(name_ru__iexact=check_name) | Q(name_en__iexact=check_name)
            ).exclude(pk=product_id).exists():
                raise ValueError("Товар с таким именем уже существует в этой категории")

            if category_id:
                from categories.models import Category
                try:
                    product.category = Category.objects.get(pk=category_id)
                except Category.DoesNotExist:
                    raise ValueError("Категория не найдена")

            if img is not None:
                product.img = img

            product.save()

            logger.info(f"Товар обновлен: {product_id} (пользователь: {user.email}) | "
                        f"RU: {product.name_ru} | EN: {product.name_en}")
            return product
    
    @staticmethod
    def get_products_by_ids(product_ids: list) -> QuerySet:
        """
        Получить товары по списку ID.

        Аргументы:
            product_ids: Список ID товаров

        Возвращает:
            QuerySet: Товары, отсортированные по порядку в списке ID
        """
        if not product_ids:
            return Product.objects.none()
        
        queryset = Product.objects.select_related('category').filter(id__in=product_ids)
        
        # Сохраняем порядок ID в результатах
        preserved_order = Case(*[When(id=id, then=pos) for pos, id in enumerate(product_ids)])
        return queryset.order_by(preserved_order)

    @staticmethod
    @transaction.atomic
    def delete_product(user: User, product_id: int) -> bool:
        """
        Удалить товар.
        
        Аргументы:
            user: Пользователь, выполняющий операцию
            product_id: ID товара
            
        Возвращает:
            bool: True если удаление успешно
            
        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если товар не найден
        """
        if not ProductService._is_admin(user):
            raise PermissionError("Только администраторы могут удалять товары")
        
        product = ProductService.get_product_detail(product_id)
        product_name = product.name
        product.delete()
        logger.info(f"Товар удален: '{product_name}' (пользователь: {user.email})")
        return True