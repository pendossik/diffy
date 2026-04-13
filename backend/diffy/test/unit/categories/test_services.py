"""Тесты бизнес-логики CategoryService."""
import pytest
from categories.services import CategoryService
from categories.models import Category


pytestmark = pytest.mark.django_db


# =============================================================================
# 🔴 CRITICAL: Тесты критических уязвимостей
# =============================================================================

class TestIsAdmin:
    """Тесты проверки прав администратора (_is_admin)."""

    def test_admin_user_returns_true(self, admin):
        """Пользователь с ролью admin проходит проверку."""
        assert CategoryService._is_admin(admin) is True

    def test_superuser_returns_true(self, superuser):
        """Суперпользователь проходит проверку."""
        assert CategoryService._is_admin(superuser) is True

    def test_regular_user_returns_false(self, user):
        """Обычный пользователь не проходит проверку."""
        assert CategoryService._is_admin(user) is False

    def test_inactive_user_returns_false(self, inactive_user):
        """Неактивный пользователь не проходит проверку."""
        assert CategoryService._is_admin(inactive_user) is False

    def test_none_user_returns_false(self):
        """None пользователь не проходит проверку (CRITICAL #1)."""
        assert CategoryService._is_admin(None) is False

    def test_anonymous_user_returns_false(self):
        """Анонимный пользователь не проходит проверку."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        anonymous = User()
        assert CategoryService._is_admin(anonymous) is False

    def test_user_without_role_attribute(self, user_factory):
        """Пользователь без role (но с is_staff=False) не проходит проверку."""
        # role NOT NULL в БД, поэтому тестируем с дефолтным значением
        custom_user = user_factory(role='user')
        custom_user.is_staff = False
        custom_user.is_superuser = False
        assert CategoryService._is_admin(custom_user) is False


class TestCreateCategoryRaceCondition:
    """Тесты защиты от race condition при создании (CRITICAL #2)."""

    def test_create_unique_name_success(self, admin):
        """Создание категории с уникальным именем успешно."""
        category = CategoryService.create_category(admin, 'Уникальная категория')
        
        assert category.id is not None
        assert category.name == 'Уникальная категория'
        assert Category.objects.filter(id=category.id).exists()

    def test_create_duplicate_name_raises_error(self, admin, category):
        """Попытка создать дубликат имени вызывает ошибку (CRITICAL #2)."""
        with pytest.raises(ValueError, match='Категория с таким именем уже существует'):
            CategoryService.create_category(admin, category.name)

    def test_create_duplicate_case_insensitive(self, admin, category):
        """Дубликат с другим регистром тоже отклоняется."""
        with pytest.raises(ValueError, match='Категория с таким именем уже существует'):
            CategoryService.create_category(admin, category.name.upper())

    def test_create_name_too_long_raises_error(self, admin):
        """Имя длиннее 100 символов отклоняется (CRITICAL #3)."""
        long_name = 'А' * 101
        with pytest.raises(ValueError, match='не должно превышать 100 символов'):
            CategoryService.create_category(admin, long_name)

    def test_create_empty_name_raises_error(self, admin):
        """Пустое имя отклоняется (CRITICAL #3)."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            CategoryService.create_category(admin, '')

    def test_create_whitespace_only_name_raises_error(self, admin):
        """Имя только с пробелами отклоняется."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            CategoryService.create_category(admin, '   ')

    def test_create_strips_and_capitalizes_name(self, admin):
        """Имя очищается от пробелов и капитализируется."""
        category = CategoryService.create_category(admin, '  тестовая категория  ')
        
        assert category.name == 'Тестовая категория'

    def test_create_non_admin_raises_permission_error(self, user):
        """Обычный пользователь не может создавать категории."""
        with pytest.raises(PermissionError, match='Только администраторы могут создавать категории'):
            CategoryService.create_category(user, 'Новая категория')


class TestUpdateCategoryRaceCondition:
    """Тесты защиты от race condition при обновлении (CRITICAL #2)."""

    def test_update_same_name_success(self, admin, category):
        """Обновление с тем же именем успешно."""
        updated = CategoryService.update_category(admin, category.id, category.name)
        
        assert updated.id == category.id
        assert updated.name == category.name

    def test_update_to_duplicate_name_raises_error(self, admin, category, duplicate_category):
        """Обновление до имени существующей категории вызывает ошибку."""
        with pytest.raises(ValueError, match='Категория с таким именем уже существует'):
            CategoryService.update_category(admin, category.id, duplicate_category.name)

    def test_update_name_too_long_raises_error(self, admin, category):
        """Слишком длинное имя отклоняется (CRITICAL #3)."""
        long_name = 'А' * 101
        with pytest.raises(ValueError, match='не должно превышать 100 символов'):
            CategoryService.update_category(admin, category.id, long_name)

    def test_update_empty_name_raises_error(self, admin, category):
        """Пустое имя отклоняется (CRITICAL #3)."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            CategoryService.update_category(admin, category.id, '')

    def test_update_non_admin_raises_permission_error(self, user, category):
        """Обычный пользователь не может обновлять категории."""
        with pytest.raises(PermissionError, match='Только администраторы могут изменять категории'):
            CategoryService.update_category(user, category.id, 'Новое имя')

    def test_update_nonexistent_category_raises_error(self, admin):
        """Обновление несуществующей категории вызывает ошибку."""
        with pytest.raises(ValueError, match='Категория не найдена'):
            CategoryService.update_category(admin, 99999, 'Новое имя')


# =============================================================================
# 🟠 HIGH: Тесты функциональности сервисов
# =============================================================================

class TestGetCategoriesList:
    """Тесты получения списка категорий."""

    def test_get_list_empty(self):
        """Пустой список возвращается корректно."""
        queryset = CategoryService.get_categories_list()
        
        assert queryset.count() == 0

    def test_get_list_returns_all_sorted(self, categories_batch):
        """Все категории возвращаются отсортированными по имени."""
        queryset = CategoryService.get_categories_list()
        
        assert queryset.count() == len(categories_batch)
        names = [cat.name for cat in queryset]
        assert names == sorted(names)

    def test_search_by_name_ru(self, categories_batch):
        """Поиск по русскому названию работает."""
        queryset = CategoryService.get_categories_list('электрон')
        
        assert queryset.count() == 1
        assert queryset.first().name_ru == 'Электроника'

    def test_search_by_name_en(self, categories_batch):
        """Поиск по английскому названию работает."""
        queryset = CategoryService.get_categories_list('phone')
        
        assert queryset.count() == 1
        assert queryset.first().name_en == 'Phones'  # name_en хранит английское значение

    def test_search_case_insensitive(self, categories_batch):
        """Поиск регистронезависимый."""
        queryset_ru = CategoryService.get_categories_list('ЭЛЕКТРОНИКА')
        queryset_en = CategoryService.get_categories_list('electronics')
        
        assert queryset_ru.count() == 1
        assert queryset_en.count() == 1

    def test_search_empty_string_returns_all(self, categories_batch):
        """Пустой поиск возвращает все категории."""
        queryset = CategoryService.get_categories_list('')
        
        assert queryset.count() == len(categories_batch)

    def test_search_whitespace_only_returns_all(self, categories_batch):
        """Поиск только с пробелами возвращает все категории."""
        queryset = CategoryService.get_categories_list('   ')
        
        assert queryset.count() == len(categories_batch)

    def test_search_partial_match(self, categories_batch):
        """Частичное совпадение работает."""
        queryset = CategoryService.get_categories_list('кни')
        
        assert queryset.count() == 1
        assert 'Книги' in queryset.first().name_ru


class TestGetCategoryDetail:
    """Тесты получения деталей категории."""

    def test_get_detail_success(self, category):
        """Успешное получение категории по ID."""
        result = CategoryService.get_category_detail(category.id)
        
        assert result.id == category.id
        assert result.name == category.name

    def test_get_detail_nonexistent_id_raises_error(self):
        """Запрос несуществующей категории вызывает ошибку."""
        with pytest.raises(ValueError, match='Категория не найдена'):
            CategoryService.get_category_detail(99999)


class TestDeleteCategory:
    """Тесты удаления категории."""

    def test_delete_success(self, admin, category):
        """Успешное удаление категории."""
        result = CategoryService.delete_category(admin, category.id)

        assert result is True
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_non_admin_raises_permission_error(self, user, category):
        """Обычный пользователь не может удалять категории."""
        with pytest.raises(PermissionError, match='Только администраторы могут удалять категории'):
            CategoryService.delete_category(user, category.id)

    def test_delete_nonexistent_category_raises_error(self, admin):
        """Удаление несуществующей категории вызывает ошибку."""
        with pytest.raises(ValueError, match='Категория не найдена'):
            CategoryService.delete_category(admin, 99999)

    def test_delete_category_with_products_raises_error(self, admin):
        """
        CR-4: Нельзя удалить категорию, в которой есть товары.
        """
        from categories.models import Category
        from products.models import Product

        category = Category.objects.create(name_ru='С товарами', name_en='With Products')
        Product.objects.create(
            name_ru='Товар в категории',
            name_en='Product in category',
            category=category
        )

        with pytest.raises(ValueError, match='Невозможно удалить категорию'):
            CategoryService.delete_category(admin, category.id)

    def test_delete_category_with_char_groups_raises_error(self, admin):
        """
        CR-4: Нельзя удалить категорию с группами характеристик.
        """
        from categories.models import Category
        from characteristic.models import CharacteristicGroup

        category = Category.objects.create(name_ru='Техника', name_en='Electronics')
        CharacteristicGroup.objects.create(
            category=category,
            name_ru='Общие',
            name_en='General'
        )

        with pytest.raises(ValueError, match='Невозможно удалить категорию'):
            CategoryService.delete_category(admin, category.id)

    def test_delete_empty_category_success(self, admin):
        """
        CR-4: Пустую категорию можно удалить.
        """
        from categories.models import Category
        category = Category.objects.create(name_ru='Пустая', name_en='Empty')

        result = CategoryService.delete_category(admin, category.id)

        assert result is True
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_category_with_products_logs_warning(self, admin, caplog):
        """
        CR-4: При попытке удалить категорию с продуктами — warning в логе.
        """
        import logging
        from categories.models import Category
        from products.models import Product

        logger = logging.getLogger('categories')
        logger.setLevel(logging.WARNING)

        category = Category.objects.create(name_ru='С товарами', name_en='With Products')
        Product.objects.create(
            name_ru='Товар',
            name_en='Product',
            category=category
        )

        with pytest.raises(ValueError):
            CategoryService.delete_category(admin, category.id)

        assert "Попытка удалить категорию с продуктами" in caplog.text
        assert category.name in caplog.text


# =============================================================================
# 🟡 MEDIUM: Тесты граничных случаев и интеграции
# =============================================================================

class TestCategoryServiceEdgeCases:
    """Тесты граничных случаев для CategoryService."""

    def test_create_with_special_characters(self, admin):
        """Создание категории со спецсимволами в имени."""
        category = CategoryService.create_category(admin, 'Тест-Категория!@#$%')
        
        assert category.name == 'Тест-категория!@#$%'

    def test_create_with_cyrillic_and_numbers(self, admin):
        """Создание категории с кириллицей и цифрами."""
        category = CategoryService.create_category(admin, 'Тест 123 Категория')
        
        assert '123' in category.name

    def test_update_preserves_id(self, admin, category):
        """Обновление сохраняет ID категории."""
        original_id = category.id
        updated = CategoryService.update_category(admin, category.id, 'Новое имя')
        
        assert updated.id == original_id

    def test_delete_returns_bool(self, admin, category):
        """Удаление возвращает bool True."""
        result = CategoryService.delete_category(admin, category.id)
        
        assert isinstance(result, bool)
        assert result is True

    def test_create_category_exists_in_db(self, admin):
        """Созданная категория действительно в БД."""
        category = CategoryService.create_category(admin, 'Тест')
        
        assert Category.objects.filter(id=category.id).exists()
        db_category = Category.objects.get(id=category.id)
        assert db_category.name == category.name

    def test_get_categories_list_is_queryset(self):
        """get_categories_list возвращает QuerySet."""
        from django.db.models import QuerySet
        
        result = CategoryService.get_categories_list()
        
        assert isinstance(result, QuerySet)

    def test_update_with_same_name_does_not_change(self, admin, category):
        """Обновление тем же именем не меняет данные."""
        original_name = category.name
        updated = CategoryService.update_category(admin, category.id, original_name)
        
        assert updated.name == original_name

    def test_create_multiple_categories_transaction(self, admin):
        """Создание нескольких категорий работает корректно."""
        cat1 = CategoryService.create_category(admin, 'Категория 1')
        cat2 = CategoryService.create_category(admin, 'Категория 2')
        
        assert cat1.id != cat2.id
        assert Category.objects.count() == 2


class TestCategoryServiceLogging:
    """Тесты логирования (проверка что логи вызываются)."""

    def test_create_logs_info_message(self, admin, caplog):
        """Создание категории логируется."""
        import logging
        logger = logging.getLogger('categories')
        logger.setLevel(logging.INFO)
        
        CategoryService.create_category(admin, 'Тестовая')
        
        assert 'Категория создана' in caplog.text
        assert 'Тестовая' in caplog.text

    def test_update_logs_info_message(self, admin, category, caplog):
        """Обновление категории логируется."""
        import logging
        logger = logging.getLogger('categories')
        logger.setLevel(logging.INFO)
        
        CategoryService.update_category(admin, category.id, 'Обновлённая')
        
        assert 'Категория обновлена' in caplog.text

    def test_delete_logs_info_message(self, admin, category, caplog):
        """Удаление категории логируется."""
        import logging
        logger = logging.getLogger('categories')
        logger.setLevel(logging.INFO)
        
        CategoryService.delete_category(admin, category.id)
        
        assert 'Категория удалена' in caplog.text
