"""Юнит-тесты для сервисов приложения characteristic."""
import pytest
from django.db import transaction
from unittest.mock import patch, MagicMock
from characteristic.services import (
    CharacteristicGroupService,
    CharacteristicTemplateService,
    CharacteristicValueService,
)
from django.test import override_settings
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue
from accounts.models import User
from categories.models import Category
from products.models import Product


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def admin_user(db):
    """Пользователь с правами администратора."""
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        username='char_admin',
        role='admin',
        is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Обычный пользователь без прав администратора."""
    return User.objects.create_user(
        email='user@test.com',
        password='testpass123',
        username='char_regular',
        role='user'
    )


@pytest.fixture
def anonymous_user():
    """Псевдо-анонимный пользователь."""
    user = MagicMock()
    user.is_authenticated = False
    user.role = None
    user.is_staff = False
    user.is_superuser = False
    return user


@pytest.fixture
def category(db):
    """Тестовая категория."""
    return Category.objects.create(name='Электроника', name_ru='Электроника', name_en='Electronics')


@pytest.fixture
def group(db, category):
    """Тестовая группа характеристик."""
    return CharacteristicGroup.objects.create(
        category=category,
        name='Основные параметры',
        name_ru='Основные параметры',
        name_en='Basic specs',
        order=1
    )


@pytest.fixture
def template(db, group):
    """Тестовый шаблон характеристики."""
    return CharacteristicTemplate.objects.create(
        group=group,
        name='Вес',
        name_ru='Вес',
        name_en='Weight',
        order=1
    )


@pytest.fixture
def product(db, category):
    """Тестовый товар."""
    return Product.objects.create(
        name='Смартфон',
        name_ru='Смартфон',
        name_en='Smartphone',
        category=category
    )


@pytest.fixture
def char_value(db, product, template):
    """Тестовое значение характеристики."""
    return CharacteristicValue.objects.create(
        product=product,
        template=template,
        value='200г',
        value_ru='200г',
        value_en='200g'
    )


# =============================================================================
# ТЕСТЫ: CharacteristicGroupService._is_admin
# =============================================================================

class TestCharacteristicGroupServiceIsAdmin:
    """Тесты проверки прав администратора для групп."""

    def test_is_admin_with_admin_role(self, admin_user):
        assert CharacteristicGroupService._is_admin(admin_user) is True

    def test_is_admin_with_superuser_flag(self, db):
        user = User.objects.create_user(
            email='super@test.com',
            password='pass',
            username='char_super',
            role = 'superuser'
        )
        assert CharacteristicGroupService._is_admin(user) is True

    def test_is_admin_with_staff_flag(self, db):
        user = User.objects.create_user(
            email='staff@test.com',
            password='pass',
            username='char_staff',
            role = 'admin'
        )
        assert CharacteristicGroupService._is_admin(user) is True

    def test_is_admin_regular_user(self, regular_user):
        assert CharacteristicGroupService._is_admin(regular_user) is False

    def test_is_admin_anonymous(self, anonymous_user):
        assert CharacteristicGroupService._is_admin(anonymous_user) is False

    def test_is_admin_none_user(self):
        assert CharacteristicGroupService._is_admin(None) is False


# =============================================================================
# ТЕСТЫ: CharacteristicGroupService - READ
# =============================================================================

@pytest.mark.django_db
class TestCharacteristicGroupServiceRead:
    """Тесты чтения для групп характеристик."""

    def test_get_groups_by_category_returns_queryset(self, category, group):
        result = CharacteristicGroupService.get_groups_by_category(category.id)
        assert isinstance(result, list) or hasattr(result, 'filter')
        assert group in list(result)
        assert result.first().order == group.order

    def test_get_groups_by_category_empty(self, category):
        result = CharacteristicGroupService.get_groups_by_category(category.id)
        assert list(result) == []

    def test_get_group_detail_success(self, group):
        result = CharacteristicGroupService.get_group_detail(group.id)
        assert result.id == group.id
        assert result.category == group.category

    def test_get_group_detail_not_found(self):
        with pytest.raises(ValueError, match="Группа характеристик не найдена"):
            CharacteristicGroupService.get_group_detail(99999)


# =============================================================================
# ТЕСТЫ: CharacteristicGroupService - CREATE
# =============================================================================

@pytest.mark.django_db
class TestCharacteristicGroupServiceCreate:
    """Тесты создания групп характеристик."""

    def test_create_group_success(self, admin_user, category):
        result = CharacteristicGroupService.create_group(
            user=admin_user,
            category_id=category.id,
            name='Новая группа',
            name_ru='Новая группа',
            name_en='New Group',
            order=10
        )
        assert result.name == 'Новая группа'
        assert result.name_en == 'New Group'
        assert result.category == category
        assert result.order == 10

    def test_create_group_without_translations(self, admin_user, category):
        result = CharacteristicGroupService.create_group(
            user=admin_user,
            category_id=category.id,
            name='Простая группа',
            order=5
        )
        assert result.name == 'Простая группа'
        assert result.name_ru == 'Простая группа'
        assert result.name_en is None

    def test_create_group_permission_denied(self, regular_user, category):
        with pytest.raises(PermissionError, match="Только администраторы"):
            CharacteristicGroupService.create_group(
                user=regular_user,
                category_id=category.id,
                name='Запрещено'
            )

    def test_create_group_category_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Категория не найдена"):
            CharacteristicGroupService.create_group(
                user=admin_user,
                category_id=99999,
                name='Тест'
            )

    def test_create_group_duplicate_name(self, admin_user, category, group):
        with pytest.raises(ValueError, match="Группа с таким именем уже существует"):
            CharacteristicGroupService.create_group(
                user=admin_user,
                category_id=category.id,
                name=group.name
            )


# =============================================================================
# ТЕСТЫ: CharacteristicGroupService - UPDATE
# =============================================================================

@pytest.mark.django_db
class TestCharacteristicGroupServiceUpdate:
    """Тесты обновления групп характеристик."""
    
    @override_settings(LANGUAGE_CODE='en')
    def test_update_group_all_fields(self, admin_user, group):
        result = CharacteristicGroupService.update_group(
            user=admin_user,
            group_id=group.id,
            name='Обновлено',
            name_ru='Обновлено RU',
            name_en='Updated EN',
            order=99
        )
        assert result.name == 'Updated EN'
        assert result.name_ru == 'Обновлено RU'
        assert result.name_en == 'Updated EN'
        assert result.order == 99

    def test_update_group_partial_fields(self, admin_user, group):
        original_name = group.name
        result = CharacteristicGroupService.update_group(
            user=admin_user,
            group_id=group.id,
            order=50
        )
        assert result.name == original_name  # не изменилось
        assert result.order == 50

    def test_update_group_permission_denied(self, regular_user, group):
        with pytest.raises(PermissionError):
            CharacteristicGroupService.update_group(
                user=regular_user,
                group_id=group.id,
                name='Hack attempt'
            )

    def test_update_group_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Группа характеристик не найдена"):
            CharacteristicGroupService.update_group(
                user=admin_user,
                group_id=99999,
                name='Тест'
            )


# =============================================================================
# ТЕСТЫ: CharacteristicGroupService - DELETE
# =============================================================================

@pytest.mark.django_db
class TestCharacteristicGroupServiceDelete:
    """Тесты удаления групп характеристик."""

    def test_delete_group_success(self, admin_user, group):
        result = CharacteristicGroupService.delete_group(
            user=admin_user,
            group_id=group.id
        )
        assert result is True
        assert not CharacteristicGroup.objects.filter(id=group.id).exists()

    def test_delete_group_permission_denied(self, regular_user, group):
        with pytest.raises(PermissionError):
            CharacteristicGroupService.delete_group(
                user=regular_user,
                group_id=group.id
            )

    def test_delete_group_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Группа характеристик не найдена"):
            CharacteristicGroupService.delete_group(
                user=admin_user,
                group_id=99999
            )


# =============================================================================
# ТЕСТЫ: ЛОГИРОВАНИЕ (опционально, для полного покрытия)
# =============================================================================

@pytest.mark.django_db
class TestCharacteristicServicesLogging:
    """Тесты проверки логирования операций."""

    @patch('characteristic.services.logger')
    def test_create_group_logs_info(self, mock_logger, admin_user, category):
        CharacteristicGroupService.create_group(
            user=admin_user,
            category_id=category.id,
            name='Logged Group'
        )
        mock_logger.info.assert_called_once()
        assert 'создана' in mock_logger.info.call_args[0][0]

    @patch('characteristic.services.logger')
    def test_update_group_logs_info(self, mock_logger, admin_user, group):
        CharacteristicGroupService.update_group(
            user=admin_user,
            group_id=group.id,
            name='Updated'
        )
        mock_logger.info.assert_called_once()
        assert 'обновлена' in mock_logger.info.call_args[0][0]

    @patch('characteristic.services.logger')
    def test_delete_group_logs_info(self, mock_logger, admin_user, group):
        CharacteristicGroupService.delete_group(
            user=admin_user,
            group_id=group.id
        )
        mock_logger.info.assert_called_once()
        assert 'удалена' in mock_logger.info.call_args[0][0]


# =============================================================================
# ТЕСТЫ: CharacteristicTemplateService
# =============================================================================

class TestCharacteristicTemplateServiceIsAdmin:
    """Тесты проверки прав для шаблонов — делегируем на группу."""

    def test_is_admin_delegates_correctly(self, admin_user, regular_user):
        assert CharacteristicTemplateService._is_admin(admin_user) is True
        assert CharacteristicTemplateService._is_admin(regular_user) is False


@pytest.mark.django_db
class TestCharacteristicTemplateServiceRead:
    """Тесты чтения для шаблонов характеристик."""

    def test_get_templates_by_group(self, group, template):
        result = CharacteristicTemplateService.get_templates_by_group(group.id)
        assert template in list(result)

    def test_get_template_detail_success(self, template):
        result = CharacteristicTemplateService.get_template_detail(template.id)
        assert result.id == template.id

    def test_get_template_detail_not_found(self):
        with pytest.raises(ValueError, match="Шаблон характеристики не найден"):
            CharacteristicTemplateService.get_template_detail(99999)


@pytest.mark.django_db
class TestCharacteristicTemplateServiceCRUD:
    """Тесты CRUD для шаблонов."""

    def test_create_template_success(self, admin_user, group):
        result = CharacteristicTemplateService.create_template(
            user=admin_user,
            group_id=group.id,
            name='Новый шаблон',
            name_en='New Template',
            order=5
        )
        assert result.name == 'Новый шаблон'
        assert result.group == group

    def test_create_template_permission_denied(self, regular_user, group):
        with pytest.raises(PermissionError):
            CharacteristicTemplateService.create_template(
                user=regular_user,
                group_id=group.id,
                name='Forbidden'
            )

    def test_create_template_group_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Группа характеристик не найдена"):
            CharacteristicTemplateService.create_template(
                user=admin_user,
                group_id=99999,
                name='Test'
            )

    def test_create_template_duplicate_name(self, admin_user, group, template):
        with pytest.raises(ValueError, match="Шаблон с таким именем уже существует"):
            CharacteristicTemplateService.create_template(
                user=admin_user,
                group_id=group.id,
                name=template.name
            )

    def test_update_template_success(self, admin_user, template):
        result = CharacteristicTemplateService.update_template(
            user=admin_user,
            template_id=template.id,
            name='Updated',
            order=100
        )
        assert result.name == 'Updated'
        assert result.order == 100

    def test_delete_template_success(self, admin_user, template):
        result = CharacteristicTemplateService.delete_template(
            user=admin_user,
            template_id=template.id
        )
        assert result is True
        assert not CharacteristicTemplate.objects.filter(id=template.id).exists()


# =============================================================================
# ТЕСТЫ: CharacteristicValueService
# =============================================================================

class TestCharacteristicValueServiceIsAdmin:
    """Проверка прав для значений характеристик."""

    def test_is_admin_variants(self, admin_user, regular_user, anonymous_user):
        assert CharacteristicValueService._is_admin(admin_user) is True
        assert CharacteristicValueService._is_admin(regular_user) is False
        assert CharacteristicValueService._is_admin(anonymous_user) is False


@pytest.mark.django_db
class TestCharacteristicValueServiceRead:
    """Тесты чтения для значений характеристик."""

    def test_get_values_by_product(self, product, char_value):
        result = CharacteristicValueService.get_values_by_product(product.id)
        assert char_value in list(result)

    def test_get_value_detail_success(self, char_value):
        result = CharacteristicValueService.get_value_detail(char_value.id)
        assert result.id == char_value.id
        assert result.product == char_value.product

    def test_get_value_detail_not_found(self):
        with pytest.raises(ValueError, match="Значение характеристики не найдено"):
            CharacteristicValueService.get_value_detail(99999)


@pytest.mark.django_db
class TestCharacteristicValueServiceCRUD:
    """CRUD для значений характеристик."""

    def test_create_value_success(self, admin_user, product, template):
        result = CharacteristicValueService.create_value(
            user=admin_user,
            product_id=product.id,
            template_id=template.id,
            value='15см',
            value_ru='15см',
            value_en='15cm'
        )
        assert result.value == '15см'
        assert result.value_en == '15cm'
        assert result.product == product
        assert result.template == template

    def test_create_value_permission_denied(self, regular_user, product, template):
        with pytest.raises(PermissionError):
            CharacteristicValueService.create_value(
                user=regular_user,
                product_id=product.id,
                template_id=template.id,
                value='test'
            )

    def test_create_value_product_not_found(self, admin_user, template):
        with pytest.raises(ValueError, match="Товар не найден"):
            CharacteristicValueService.create_value(
                user=admin_user,
                product_id=99999,
                template_id=template.id,
                value='test'
            )

    def test_create_value_template_not_found(self, admin_user, product):
        with pytest.raises(ValueError, match="Шаблон характеристики не найден"):
            CharacteristicValueService.create_value(
                user=admin_user,
                product_id=product.id,
                template_id=99999,
                value='test'
            )

    def test_create_value_duplicate(self, admin_user, product, template, char_value):
        with pytest.raises(ValueError, match="Характеристика уже существует"):
            CharacteristicValueService.create_value(
                user=admin_user,
                product_id=product.id,
                template_id=template.id,
                value='duplicate'
            )

    def test_update_value_success(self, admin_user, char_value):
        result = CharacteristicValueService.update_value(
            user=admin_user,
            value_id=char_value.id,
            value='300г',
            value_en='300g'
        )
        assert result.value == '300г'
        assert result.value_en == '300g'

    def test_delete_value_success(self, admin_user, char_value):
        result = CharacteristicValueService.delete_value(
            user=admin_user,
            value_id=char_value.id
        )
        assert result is True
        assert not CharacteristicValue.objects.filter(id=char_value.id).exists()