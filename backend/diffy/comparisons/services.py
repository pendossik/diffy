"""Бизнес-логика приложения comparisons."""
from django.db import transaction
from django.db.models import QuerySet
import logging
from .models import FavoriteComparison
from accounts.models import User
from products.services import ProductService
from characteristic.services import CharacteristicValueService

logger = logging.getLogger('comparisons')


class FavoriteComparisonService:
    """
    Сервисный класс для операций с избранными сравнениями.

    Все методы статические; операции записи — транзакционные.
    """

    @staticmethod
    def _generate_products_hash(product_ids: list) -> str:
        """
        Сгенерировать хеш для набора товаров.

        Сортирует ID чтобы наборы [1,2] и [2,1] имели одинаковый хеш.

        Аргументы:
            product_ids: Список ID товаров

        Возвращает:
            str: Хеш строка
        """
        sorted_ids = sorted(product_ids)
        return ','.join(map(str, sorted_ids))

    @staticmethod
    def get_user_comparisons(user: User) -> QuerySet:
        """
        Получить все избранные сравнения пользователя.

        Аргументы:
            user: Пользователь

        Возвращает:
            QuerySet: Избранные сравнения, отсортированные по дате создания
        """
        return FavoriteComparison.objects.filter(
            user=user
        ).select_related('user').prefetch_related('products').order_by('-created_at')

    @staticmethod
    def get_comparison_detail(user: User, comparison_id: int) -> FavoriteComparison:
        """
        Получить детали одного сравнения.

        Аргументы:
            user: Пользователь (для проверки прав)
            comparison_id: ID сравнения

        Возвращает:
            FavoriteComparison: Экземпляр сравнения

        Исключения:
            ValueError: Если сравнение не найдено или не принадлежит пользователю
        """
        try:
            comparison = FavoriteComparison.objects.select_related('user').prefetch_related(
                'products'
            ).get(pk=comparison_id)

            # Проверка что сравнение принадлежит пользователю
            if comparison.user != user:
                raise ValueError("У вас нет доступа к этому сравнению")

            return comparison
        except FavoriteComparison.DoesNotExist:
            raise ValueError("Сравнение не найдено")

    @staticmethod
    @transaction.atomic
    def add_to_favorites(user: User, product_ids: list) -> FavoriteComparison:
        """
        Добавить набор товаров в избранные сравнения.

        Аргументы:
            user: Пользователь
            product_ids: Список ID товаров для сравнения

        Возвращает:
            FavoriteComparison: Созданное избранное сравнение

        Исключения:
            ValueError: Если товары не найдены или дубликат уже существует
        """
        if not product_ids or len(product_ids) < 2:
            raise ValueError("Для сравнения необходимо минимум 2 товара")

        # Проверяем существование товаров
        products = ProductService.get_products_by_ids(product_ids)
        if products.count() != len(product_ids):
            raise ValueError("Один или несколько товаров не найдены")

        # Генерируем хеш для проверки на дубликаты
        products_hash = FavoriteComparisonService._generate_products_hash(product_ids)

        # Проверяем на дубликаты
        if FavoriteComparison.objects.filter(
            user=user,
            products_hash=products_hash
        ).exists():
            logger.warning(
                f"Попытка добавить дубликат в избранное: "
                f"пользователь {user.email}, товары: {product_ids}"
            )
            raise ValueError("Такое сравнение уже есть в избранных")

        # Создаём избранное сравнение
        comparison = FavoriteComparison.objects.create(
            user=user,
            products_hash=products_hash
        )

        # Добавляем товары
        comparison.products.set(products)

        logger.info(
            f"Добавлено в избранное: пользователь {user.email}, "
            f"товары: {product_ids}"
        )

        return comparison

    @staticmethod
    @transaction.atomic
    def remove_from_favorites(user: User, comparison_id: int) -> bool:
        """
        Удалить сравнение из избранных.

        Аргументы:
            user: Пользователь (для проверки прав)
            comparison_id: ID сравнения

        Возвращает:
            bool: True если удаление успешно

        Исключения:
            ValueError: Если сравнение не найдено или не принадлежит пользователю
        """
        comparison = FavoriteComparisonService.get_comparison_detail(user, comparison_id)

        comparison.delete()

        logger.info(
            f"Удалено из избранного: пользователь {user.email}, сравнение ID={comparison_id}"
        )

        return True


class ComparisonCharacteristicsService:
    """
    Сервисный класс для сравнения товаров по характеристикам.

    Сравнивает характеристики нескольких товаров и возвращает
    структурированные данные для отображения.
    """

    @staticmethod
    def compare_products_by_characteristics(product_ids: list) -> dict:
        """
        Сравнить товары по характеристикам.

        Аргументы:
            product_ids: Список ID товаров для сравнения

        Возвращает:
            dict: Структурированные данные для сравнения

        Исключения:
            ValueError: Если товаров меньше 2 или товары не найдены
        """
        if not product_ids or len(product_ids) < 2:
            raise ValueError("Для сравнения необходимо минимум 2 товара")

        # Получаем товары
        products = ProductService.get_products_by_ids(product_ids)
        if products.count() != len(product_ids):
            raise ValueError("Один или несколько товаров не найдены")

        # Получаем характеристики для каждого товара
        products_characteristics = {}
        all_templates = {}  # Все шаблоны для объединения
        all_groups = {}  # Все группы для объединения

        for product in products:
            values = CharacteristicValueService.get_values_by_product(product.id)
            products_characteristics[product.id] = {
                'product_id': product.id,
                'product_name': product.name,
                'characteristics': {}
            }

            for value in values:
                template_id = value.template.id
                group_id = value.template.group.id

                # Сохраняем информацию о шаблоне и группе с переводами
                if template_id not in all_templates:
                    all_templates[template_id] = {
                        'template_id': template_id,
                        'template_name': value.template.name,
                        'template_name_ru': value.template.name_ru,
                        'template_name_en': value.template.name_en,
                        'group_id': group_id,
                        'group_name': value.template.group.name,
                        'group_name_ru': value.template.group.name_ru,
                        'group_name_en': value.template.group.name_en,
                        'group_order': value.template.group.order,
                        'template_order': value.template.order,
                    }

                # Сохраняем значение характеристики для товара
                products_characteristics[product.id]['characteristics'][template_id] = {
                    'value': value.value,
                    'value_ru': value.value_ru,
                    'value_en': value.value_en,
                }

                # Добавляем группу
                if group_id not in all_groups:
                    all_groups[group_id] = {
                        'group_id': group_id,
                        'group_name': value.template.group.name,
                        'group_name_ru': value.template.group.name_ru,
                        'group_name_en': value.template.group.name_en,
                        'order': value.template.group.order,
                        'templates': {}
                    }

                # Добавляем шаблон в группу
                all_groups[group_id]['templates'][template_id] = all_templates[template_id]

        # Формируем итоговую структуру
        comparison_data = {
            'products_count': len(product_ids),
            'products': [],
            'groups': []
        }

        # Добавляем информацию о товарах
        for product_id, product_data in products_characteristics.items():
            comparison_data['products'].append({
                'product_id': product_data['product_id'],
                'product_name': product_data['product_name'],
            })

        # Добавляем группы с характеристиками
        for group_id, group_data in sorted(all_groups.items(), key=lambda x: x[1]['order']):
            group_info = {
                'group_id': group_data['group_id'],
                'group_name': group_data['group_name'],
                'group_name_ru': group_data['group_name_ru'],
                'group_name_en': group_data['group_name_en'],
                'order': group_data['order'],
                'characteristics': []
            }

            for template_id, template_data in sorted(group_data['templates'].items(), key=lambda x: x[1]['template_order']):
                char_info = {
                    'template_id': template_data['template_id'],
                    'template_name': template_data['template_name'],
                    'template_name_ru': template_data['template_name_ru'],
                    'template_name_en': template_data['template_name_en'],
                    'values': {}
                }

                # Добавляем значения для каждого товара
                for product_id, product_data in products_characteristics.items():
                    if template_id in product_data['characteristics']:
                        char_info['values'][product_id] = product_data['characteristics'][template_id]
                    else:
                        char_info['values'][product_id] = {
                            'value': None,
                            'value_ru': None,
                            'value_en': None,
                        }

                group_info['characteristics'].append(char_info)

            comparison_data['groups'].append(group_info)

        return comparison_data
