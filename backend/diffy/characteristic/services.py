"""Бизнес-логика приложения characteristic."""
from django.db import transaction
from django.db.models import QuerySet
import logging
from .models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue
from accounts.models import User
from categories.models import Category
from products.models import Product

logger = logging.getLogger('characteristic')


class CharacteristicGroupService:
    """
    Сервисный класс для операций с группами характеристик.

    Все методы статические; операции записи — транзакционные.
    """

    @staticmethod
    def _is_admin(user: User) -> bool:
        """Проверка прав администратора."""
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, 'role', None) in ('admin', 'superuser') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )

    @staticmethod
    def get_groups_by_category(category_id: int) -> QuerySet:
        """
        Получить все группы характеристик категории.

        Аргументы:
            category_id: ID категории

        Возвращает:
            QuerySet: Группы характеристик, отсортированные по order
        """
        return CharacteristicGroup.objects.filter(
            category_id=category_id
        ).select_related('category').prefetch_related('templates').order_by('order')

    @staticmethod
    def get_group_detail(group_id: int) -> CharacteristicGroup:
        """
        Получить детали группы характеристик.

        Аргументы:
            group_id: ID группы

        Возвращает:
            CharacteristicGroup: Экземпляр группы

        Исключения:
            ValueError: Если группа не найдена
        """
        try:
            return CharacteristicGroup.objects.select_related(
                'category'
            ).prefetch_related('templates').get(pk=group_id)
        except CharacteristicGroup.DoesNotExist:
            raise ValueError("Группа характеристик не найдена")

    @staticmethod
    @transaction.atomic
    def create_group(user: User, category_id: int, name: str, name_ru: str = None, name_en: str = None, order: int = 0) -> CharacteristicGroup:
        """
        Создать новую группу характеристик.

        Аргументы:
            user: Пользователь, выполняющий операцию
            category_id: ID категории
            name: Название группы (для текущей локали)
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)
            order: Порядок сортировки

        Возвращает:
            CharacteristicGroup: Созданная группа

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если категория не найдена или группа с таким именем уже существует
        """
        if not CharacteristicGroupService._is_admin(user):
            raise PermissionError("Только администраторы могут создавать группы характеристик")

        # Проверяем существование категории
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError("Категория не найдена")

        # Проверяем уникальность имени в категории
        if CharacteristicGroup.objects.filter(category=category, name=name).exists():
            raise ValueError("Группа с таким именем уже существует в этой категории")

        # Создаём группу
        group = CharacteristicGroup(
            category=category,
            name=name,
            order=order
        )

        # Устанавливаем переводы если указаны
        if name_ru:
            group.name_ru = name_ru
        if name_en:
            group.name_en = name_en

        group.save()

        logger.info(f"Группа характеристик создана: '{name}' (пользователь: {user.email})")
        return group

    @staticmethod
    @transaction.atomic
    def update_group(user: User, group_id: int, name: str = None, name_ru: str = None, name_en: str = None, order: int = None) -> CharacteristicGroup:
        """
        Обновить группу характеристик.

        Аргументы:
            user: Пользователь, выполняющий операцию
            group_id: ID группы
            name: Новое название (опционально)
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)
            order: Новый порядок (опционально)

        Возвращает:
            CharacteristicGroup: Обновлённая группа

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если группа не найдена
        """
        if not CharacteristicGroupService._is_admin(user):
            raise PermissionError("Только администраторы могут изменять группы характеристик")

        group = CharacteristicGroupService.get_group_detail(group_id)

        if name is not None:
            group.name = name
        if name_ru is not None:
            group.name_ru = name_ru
        if name_en is not None:
            group.name_en = name_en
        if order is not None:
            group.order = order

        group.save()

        logger.info(f"Группа характеристик обновлена: ID={group_id} (пользователь: {user.email})")
        return group

    @staticmethod
    @transaction.atomic
    def delete_group(user: User, group_id: int) -> bool:
        """
        Удалить группу характеристик.

        Аргументы:
            user: Пользователь, выполняющий операцию
            group_id: ID группы

        Возвращает:
            bool: True если удаление успешно

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если группа не найдена
        """
        if not CharacteristicGroupService._is_admin(user):
            raise PermissionError("Только администраторы могут удалять группы характеристик")

        group = CharacteristicGroupService.get_group_detail(group_id)
        group_name = group.name
        group.delete()

        logger.info(f"Группа характеристик удалена: '{group_name}' (пользователь: {user.email})")
        return True


class CharacteristicTemplateService:
    """
    Сервисный класс для операций с шаблонами характеристик.

    Все методы статические; операции записи — транзакционные.
    """

    @staticmethod
    def _is_admin(user: User) -> bool:
        """Проверка прав администратора."""
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, 'role', None) in ('admin', 'superuser') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )

    @staticmethod
    def get_templates_by_group(group_id: int) -> QuerySet:
        """
        Получить все шаблоны характеристик группы.

        Аргументы:
            group_id: ID группы

        Возвращает:
            QuerySet: Шаблоны, отсортированные по order
        """
        return CharacteristicTemplate.objects.filter(
            group_id=group_id
        ).select_related('group').order_by('order')

    @staticmethod
    def get_template_detail(template_id: int) -> CharacteristicTemplate:
        """
        Получить детали шаблона характеристики.

        Аргументы:
            template_id: ID шаблона

        Возвращает:
            CharacteristicTemplate: Экземпляр шаблона

        Исключения:
            ValueError: Если шаблон не найден
        """
        try:
            return CharacteristicTemplate.objects.select_related('group').get(pk=template_id)
        except CharacteristicTemplate.DoesNotExist:
            raise ValueError("Шаблон характеристики не найден")

    @staticmethod
    @transaction.atomic
    def create_template(user: User, group_id: int, name: str, name_ru: str = None, name_en: str = None, order: int = 0) -> CharacteristicTemplate:
        """
        Создать новый шаблон характеристики.

        Аргументы:
            user: Пользователь, выполняющий операцию
            group_id: ID группы
            name: Название характеристики
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)
            order: Порядок сортировки

        Возвращает:
            CharacteristicTemplate: Созданный шаблон

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если группа не найдена или шаблон с таким именем уже существует
        """
        if not CharacteristicTemplateService._is_admin(user):
            raise PermissionError("Только администраторы могут создавать шаблоны характеристик")

        # Проверяем существование группы
        try:
            group = CharacteristicGroup.objects.get(pk=group_id)
        except CharacteristicGroup.DoesNotExist:
            raise ValueError("Группа характеристик не найдена")

        # Проверяем уникальность имени в группе
        if CharacteristicTemplate.objects.filter(group=group, name=name).exists():
            raise ValueError("Шаблон с таким именем уже существует в этой группе")

        # Создаём шаблон
        template = CharacteristicTemplate(
            group=group,
            name=name,
            order=order
        )

        # Устанавливаем переводы если указаны
        if name_ru:
            template.name_ru = name_ru
        if name_en:
            template.name_en = name_en

        template.save()

        logger.info(f"Шаблон характеристики создан: '{name}' (пользователь: {user.email})")
        return template

    @staticmethod
    @transaction.atomic
    def update_template(user: User, template_id: int, name: str = None, name_ru: str = None, name_en: str = None, order: int = None) -> CharacteristicTemplate:
        """
        Обновить шаблон характеристики.

        Аргументы:
            user: Пользователь, выполняющий операцию
            template_id: ID шаблона
            name: Новое название (опционально)
            name_ru: Русское название (опционально)
            name_en: Английское название (опционально)
            order: Новый порядок (опционально)

        Возвращает:
            CharacteristicTemplate: Обновлённый шаблон

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если шаблон не найден
        """
        if not CharacteristicTemplateService._is_admin(user):
            raise PermissionError("Только администраторы могут изменять шаблоны характеристик")

        template = CharacteristicTemplateService.get_template_detail(template_id)

        if name is not None:
            template.name = name
        if name_ru is not None:
            template.name_ru = name_ru
        if name_en is not None:
            template.name_en = name_en
        if order is not None:
            template.order = order

        template.save()

        logger.info(f"Шаблон характеристики обновлён: ID={template_id} (пользователь: {user.email})")
        return template

    @staticmethod
    @transaction.atomic
    def delete_template(user: User, template_id: int) -> bool:
        """
        Удалить шаблон характеристики.

        Аргументы:
            user: Пользователь, выполняющий операцию
            template_id: ID шаблона

        Возвращает:
            bool: True если удаление успешно

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если шаблон не найден
        """
        if not CharacteristicTemplateService._is_admin(user):
            raise PermissionError("Только администраторы могут удалять шаблоны характеристик")

        template = CharacteristicTemplateService.get_template_detail(template_id)
        template_name = template.name
        template.delete()

        logger.info(f"Шаблон характеристики удалён: '{template_name}' (пользователь: {user.email})")
        return True


class CharacteristicValueService:
    """
    Сервисный класс для операций со значениями характеристик.

    Все методы статические; операции записи — транзакционные.
    """

    @staticmethod
    def _is_admin(user: User) -> bool:
        """Проверка прав администратора."""
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, 'role', None) in ('admin', 'superuser') or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )

    @staticmethod
    def get_values_by_product(product_id: int) -> QuerySet:
        """
        Получить все значения характеристик товара.

        Аргументы:
            product_id: ID товара

        Возвращает:
            QuerySet: Значения характеристик, сгруппированные по группам
        """
        return CharacteristicValue.objects.filter(
            product_id=product_id
        ).select_related('product', 'template__group').order_by('template__group__order', 'template__order')

    @staticmethod
    def get_value_detail(value_id: int) -> CharacteristicValue:
        """
        Получить детали значения характеристики.

        Аргументы:
            value_id: ID значения

        Возвращает:
            CharacteristicValue: Экземпляр значения

        Исключения:
            ValueError: Если значение не найдено
        """
        try:
            return CharacteristicValue.objects.select_related(
                'product', 'template__group'
            ).get(pk=value_id)
        except CharacteristicValue.DoesNotExist:
            raise ValueError("Значение характеристики не найдено")

    @staticmethod
    @transaction.atomic
    def create_value(user: User, product_id: int, template_id: int, value: str, value_ru: str = None, value_en: str = None) -> CharacteristicValue:
        """
        Создать значение характеристики для товара.

        Аргументы:
            user: Пользователь, выполняющий операцию
            product_id: ID товара
            template_id: ID шаблона характеристики
            value: Значение характеристики
            value_ru: Русское значение (опционально)
            value_en: Английское значение (опционально)

        Возвращает:
            CharacteristicValue: Созданное значение

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если товар или шаблон не найдены
        """
        if not CharacteristicValueService._is_admin(user):
            raise PermissionError("Только администраторы могут добавлять характеристики товаров")

        # Проверяем существование товара
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValueError("Товар не найден")

        # Проверяем существование шаблона
        try:
            template = CharacteristicTemplate.objects.get(pk=template_id)
        except CharacteristicTemplate.DoesNotExist:
            raise ValueError("Шаблон характеристики не найден")

        # Проверяем существует ли уже значение для этого товара и шаблона
        if CharacteristicValue.objects.filter(product=product, template=template).exists():
            raise ValueError("Характеристика уже существует для этого товара")

        # Создаём значение
        char_value = CharacteristicValue(
            product=product,
            template=template,
            value=value
        )

        # Устанавливаем переводы если указаны
        if value_ru:
            char_value.value_ru = value_ru
        if value_en:
            char_value.value_en = value_en

        char_value.save()

        logger.info(f"Характеристика товара создана: '{template.name}={value}' (пользователь: {user.email})")
        return char_value

    @staticmethod
    @transaction.atomic
    def update_value(user: User, value_id: int, value: str = None, value_ru: str = None, value_en: str = None) -> CharacteristicValue:
        """
        Обновить значение характеристики.

        Аргументы:
            user: Пользователь, выполняющий операцию
            value_id: ID значения
            value: Новое значение (опционально)
            value_ru: Русское значение (опционально)
            value_en: Английское значение (опционально)

        Возвращает:
            CharacteristicValue: Обновлённое значение

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если значение не найдено
        """
        if not CharacteristicValueService._is_admin(user):
            raise PermissionError("Только администраторы могут изменять характеристики товаров")

        char_value = CharacteristicValueService.get_value_detail(value_id)

        if value is not None:
            char_value.value = value
        if value_ru is not None:
            char_value.value_ru = value_ru
        if value_en is not None:
            char_value.value_en = value_en

        char_value.save()

        logger.info(f"Характеристика товара обновлена: ID={value_id} (пользователь: {user.email})")
        return char_value

    @staticmethod
    @transaction.atomic
    def delete_value(user: User, value_id: int) -> bool:
        """
        Удалить значение характеристики.

        Аргументы:
            user: Пользователь, выполняющий операцию
            value_id: ID значения

        Возвращает:
            bool: True если удаление успешно

        Исключения:
            PermissionError: Если пользователь не администратор
            ValueError: Если значение не найдено
        """
        if not CharacteristicValueService._is_admin(user):
            raise PermissionError("Только администраторы могут удалять характеристики товаров")

        char_value = CharacteristicValueService.get_value_detail(value_id)
        char_value.delete()

        logger.info(f"Характеристика товара удалена: ID={value_id} (пользователь: {user.email})")
        return True
