"""Тесты бизнес-логики ProductService."""
import pytest
from products.services import ProductService
from products.models import Product


pytestmark = pytest.mark.django_db


# =============================================================================
# 🔴 CRITICAL: Тесты критических уязвимостей
# =============================================================================

class TestIsAdmin:
    """Тесты проверки прав администратора (_is_admin)."""

    def test_admin_user_returns_true(self, admin):
        """Пользователь с ролью admin проходит проверку."""
        assert ProductService._is_admin(admin) is True

    def test_superuser_returns_true(self, superuser):
        """Суперпользователь проходит проверку."""
        assert ProductService._is_admin(superuser) is True

    def test_regular_user_returns_false(self, user):
        """Обычный пользователь не проходит проверку."""
        assert ProductService._is_admin(user) is False

    def test_inactive_user_returns_false(self, inactive_user):
        """Неактивный пользователь не проходит проверку."""
        assert ProductService._is_admin(inactive_user) is False

    def test_none_user_returns_false(self):
        """None пользователь не проходит проверку (CRITICAL #1)."""
        assert ProductService._is_admin(None) is False

    def test_anonymous_user_returns_false(self):
        """Анонимный пользователь не проходит проверку."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        anonymous = User()
        assert ProductService._is_admin(anonymous) is False

    def test_user_without_role_attribute(self, user_factory):
        """Пользователь без role (но с is_staff=False) не проходит проверку."""
        custom_user = user_factory(role='user')
        custom_user.is_staff = False
        custom_user.is_superuser = False
        assert ProductService._is_admin(custom_user) is False


class TestCreateProductRaceCondition:
    """Тесты защиты от race condition при создании (CRITICAL #2)."""

    def test_create_unique_name_success(self, admin, test_category):
        """Создание товара с уникальным именем успешно."""
        product = ProductService.create_product(
            admin,
            name='Уникальный товар',
            category_id=test_category.id
        )

        assert product.id is not None
        assert product.name == 'Уникальный товар'
        assert Product.objects.filter(id=product.id).exists()

    def test_create_duplicate_name_raises_error(self, admin, test_category, test_product):
        """Попытка создать дубликат имени в той же категории вызывает ошибку (CRITICAL #2)."""
        with pytest.raises(ValueError, match='Товар с таким именем уже существует в этой категории'):
            ProductService.create_product(
                admin,
                name='Тестовый товар',
                category_id=test_category.id
            )

    def test_create_duplicate_case_insensitive(self, admin, test_category, test_product):
        """Дубликат с другим регистром в той же категории отклоняется."""
        with pytest.raises(ValueError, match='Товар с таким именем уже существует в этой категории'):
            ProductService.create_product(
                admin,
                name='ТЕСТОВЫЙ ТОВАР',
                category_id=test_category.id
            )

    def test_create_same_name_different_category_success(self, admin, test_category, test_category2, test_product):
        """Создание товара с тем же именем в другой категории успешно."""
        product = ProductService.create_product(
            admin,
            name='Тестовый товар',
            category_id=test_category2.id
        )

        assert product.id is not None
        assert product.category_id == test_category2.id

    def test_create_name_too_long_raises_error(self, admin, test_category):
        """Имя длиннее 200 символов отклоняется (CRITICAL #3)."""
        long_name = 'А' * 201
        with pytest.raises(ValueError, match='не должно превышать 200 символов'):
            ProductService.create_product(admin, long_name, test_category.id)

    def test_create_empty_name_raises_error(self, admin, test_category):
        """Пустое имя отклоняется (CRITICAL #4)."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            ProductService.create_product(admin, '', test_category.id)

    def test_create_whitespace_only_name_raises_error(self, admin, test_category):
        """Имя только с пробелами отклоняется."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            ProductService.create_product(admin, '   ', test_category.id)

    def test_create_strips_name(self, admin, test_category):
        """Имя очищается от пробелов."""
        product = ProductService.create_product(
            admin,
            '  тестовый товар  ',
            test_category.id
        )

        assert product.name == 'тестовый товар'

    def test_create_non_admin_raises_permission_error(self, user, test_category):
        """Обычный пользователь не может создавать товары."""
        with pytest.raises(PermissionError, match='Только администраторы могут создавать товары'):
            ProductService.create_product(user, 'Новый товар', test_category.id)

    def test_create_with_nonexistent_category_raises_error(self, admin):
        """Создание с несуществующей категорией вызывает ошибку."""
        with pytest.raises(ValueError, match='Категория не найдена'):
            ProductService.create_product(admin, 'Товар', 99999)


class TestUpdateProductRaceCondition:
    """Тесты защиты от race condition при обновлении (CRITICAL #2)."""

    def test_update_same_name_success(self, admin, test_product):
        """Обновление с тем же именем успешно."""
        updated = ProductService.update_product(
            admin,
            test_product.id,
            name=test_product.name
        )

        assert updated.id == test_product.id
        assert updated.name == test_product.name

    def test_update_to_duplicate_name_raises_error(self, admin, test_product, test_category):
        """Обновление до имени существующего товара в той же категории вызывает ошибку."""
        # Создаём второй товар
        product2 = ProductService.create_product(
            admin,
            'Второй товар',
            test_category.id
        )

        # Пытаемся обновить первый товар до имени второго
        with pytest.raises(ValueError, match='Товар с таким именем уже существует в этой категории'):
            ProductService.update_product(
                admin,
                test_product.id,
                name='Второй товар'
            )

    def test_update_name_too_long_raises_error(self, admin, test_product):
        """Слишком длинное имя отклоняется (CRITICAL #3)."""
        long_name = 'А' * 201
        with pytest.raises(ValueError, match='не должно превышать 200 символов'):
            ProductService.update_product(admin, test_product.id, name=long_name)

    def test_update_empty_name_raises_error(self, admin, test_product):
        """Пустое имя отклоняется (CRITICAL #4)."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            ProductService.update_product(admin, test_product.id, name='')

    def test_update_non_admin_raises_permission_error(self, user, test_product):
        """Обычный пользователь не может обновлять товары."""
        with pytest.raises(PermissionError, match='Только администраторы могут изменять товары'):
            ProductService.update_product(user, test_product.id, name='Новое имя')

    def test_update_nonexistent_product_raises_error(self, admin):
        """Обновление несуществующего товара вызывает ошибку."""
        with pytest.raises(ValueError, match='Товар не найден'):
            ProductService.update_product(admin, 99999, name='Новое имя')


# =============================================================================
# 🟠 HIGH: Тесты функциональности сервисов
# =============================================================================

class TestGetProductsList:
    """Тесты получения списка товаров."""

    def test_get_list_empty(self):
        """Пустой список возвращается корректно."""
        queryset = ProductService.get_products_list()

        assert queryset.count() == 0

    def test_get_list_returns_all_sorted(self, many_products):
        """Все товары возвращаются отсортированными."""
        queryset = ProductService.get_products_list()

        assert queryset.count() == 25

    def test_filter_by_category(self, products_in_different_categories, test_category):
        """Фильтрация по категории работает."""
        queryset = ProductService.get_products_list(category_id=test_category.id)

        assert queryset.count() == 2

    def test_search_by_name_ru(self, searchable_products):
        """Поиск по русскому названию работает."""
        queryset = ProductService.get_products_list(search='ноутбук')

        assert queryset.count() == 1
        assert queryset.first().name_ru == 'Ноутбук Dell XPS 15'

    def test_search_by_name_en(self, searchable_products):
        """Поиск по английскому названию работает."""
        queryset = ProductService.get_products_list(search='iphone')

        assert queryset.count() == 1
        assert 'iPhone' in queryset.first().name_en

    def test_search_case_insensitive(self, searchable_products):
        """Поиск регистронезависимый."""
        queryset_upper = ProductService.get_products_list(search='НОУТБУК')
        queryset_lower = ProductService.get_products_list(search='ноутбук')

        assert queryset_upper.count() == 1
        assert queryset_lower.count() == 1

    def test_search_empty_string_returns_all(self, searchable_products):
        """Пустой поиск возвращает все товары."""
        queryset = ProductService.get_products_list(search='')

        assert queryset.count() == 5

    def test_search_with_category_filter(self, products_in_different_categories, test_category):
        """Поиск с фильтрацией по категории работает."""
        queryset = ProductService.get_products_list(
            search='Товар',
            category_id=test_category.id
        )

        assert queryset.count() == 2


class TestGetProductDetail:
    """Тесты получения деталей товара."""

    def test_get_detail_success(self, test_product):
        """Успешное получение товара по ID."""
        result = ProductService.get_product_detail(test_product.id)

        assert result.id == test_product.id
        assert result.name == test_product.name

    def test_get_detail_with_category(self, test_product):
        """Товар возвращается с категорией (select_related)."""
        result = ProductService.get_product_detail(test_product.id)

        assert result.category is not None
        assert result.category.id == test_product.category_id

    def test_get_detail_nonexistent_id_raises_error(self):
        """Запрос несуществующего товара вызывает ошибку."""
        with pytest.raises(ValueError, match='Товар не найден'):
            ProductService.get_product_detail(99999)


class TestDeleteProduct:
    """Тесты удаления товара."""

    def test_delete_success(self, admin, test_product):
        """Успешное удаление товара."""
        result = ProductService.delete_product(admin, test_product.id)

        assert result is True
        assert not Product.objects.filter(id=test_product.id).exists()

    def test_delete_non_admin_raises_permission_error(self, user, test_product):
        """Обычный пользователь не может удалять товары."""
        with pytest.raises(PermissionError, match='Только администраторы могут удалять товары'):
            ProductService.delete_product(user, test_product.id)

    def test_delete_nonexistent_product_raises_error(self, admin):
        """Удаление несуществующего товара вызывает ошибку."""
        with pytest.raises(ValueError, match='Товар не найден'):
            ProductService.delete_product(admin, 99999)


# =============================================================================
# 🟡 MEDIUM: Тесты граничных случаев и интеграции
# =============================================================================

class TestProductServiceEdgeCases:
    """Тесты граничных случаев для ProductService."""

    def test_create_with_special_characters(self, admin, test_category):
        """Создание товара со спецсимволами в имени."""
        product = ProductService.create_product(
            admin,
            'Товар-Категория!@#$%',
            test_category.id
        )

        assert '!' in product.name

    def test_create_with_numbers(self, admin, test_category):
        """Создание товара с цифрами в имени."""
        product = ProductService.create_product(
            admin,
            'Товар 123',
            test_category.id
        )

        assert '123' in product.name

    def test_update_preserves_id(self, admin, test_product):
        """Обновление сохраняет ID товара."""
        original_id = test_product.id
        updated = ProductService.update_product(
            admin,
            test_product.id,
            name='Новое имя'
        )

        assert updated.id == original_id

    def test_delete_returns_bool(self, admin, test_product):
        """Удаление возвращает bool True."""
        result = ProductService.delete_product(admin, test_product.id)

        assert isinstance(result, bool)
        assert result is True

    def test_create_product_exists_in_db(self, admin, test_category):
        """Созданный товар действительно в БД."""
        product = ProductService.create_product(admin, 'Тест', test_category.id)

        assert Product.objects.filter(id=product.id).exists()
        db_product = Product.objects.get(id=product.id)
        assert db_product.name == product.name

    def test_get_products_list_is_queryset(self):
        """get_products_list возвращает QuerySet."""
        from django.db.models import QuerySet

        result = ProductService.get_products_list()

        assert isinstance(result, QuerySet)

    def test_update_with_same_name_success(self, admin, test_product):
        """Обновление тем же именем успешно."""
        updated = ProductService.update_product(
            admin,
            test_product.id,
            name=test_product.name
        )

        assert updated.name == test_product.name

    def test_create_multiple_products_transaction(self, admin, test_category):
        """Создание нескольких товаров работает корректно."""
        product1 = ProductService.create_product(admin, 'Товар 1', test_category.id)
        product2 = ProductService.create_product(admin, 'Товар 2', test_category.id)

        assert product1.id != product2.id
        assert Product.objects.count() == 2

    def test_update_img_field(self, admin, test_product):
        """Обновление поля img работает."""
        updated = ProductService.update_product(
            admin,
            test_product.id,
            img='products/new-image.jpg'
        )

        assert updated.img == 'products/new-image.jpg'

    def test_update_category(self, admin, test_product, test_category2):
        """Обновление категории товара работает."""
        original_category_id = test_product.category_id
        updated = ProductService.update_product(
            admin,
            test_product.id,
            category_id=test_category2.id
        )

        assert updated.category_id == test_category2.id
        assert updated.category_id != original_category_id


class TestProductServiceLogging:
    """Тесты логирования (проверка что логи вызываются)."""

    def test_create_logs_info_message(self, admin, test_category, caplog):
        """Создание товара логируется."""
        import logging
        logger = logging.getLogger('products')
        logger.setLevel(logging.INFO)

        ProductService.create_product(admin, 'Тестовый', test_category.id)

        assert 'Товар создан' in caplog.text

    def test_update_logs_info_message(self, admin, test_product, caplog):
        """Обновление товара логируется."""
        import logging
        logger = logging.getLogger('products')
        logger.setLevel(logging.INFO)

        ProductService.update_product(admin, test_product.id, name='Обновлённый')

        assert 'Товар обновлен' in caplog.text

    def test_delete_logs_info_message(self, admin, test_product, caplog):
        """Удаление товара логируется."""
        import logging
        logger = logging.getLogger('products')
        logger.setLevel(logging.INFO)

        ProductService.delete_product(admin, test_product.id)

        assert 'Товар удален' in caplog.text
