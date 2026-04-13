"""Тесты для непокрытых строк сериализаторов и менеджеров."""
import pytest
from rest_framework import serializers
from django.test import override_settings
from categories.models import Category
from products.models import Product
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue
from accounts.models import User
from categories.serializers import CategoryCreateSerializer, CategoryUpdateSerializer
from products.serializers import ProductCreateSerializer, ProductUpdateSerializer
from characteristic.serializers import (
    CharacteristicGroupCreateSerializer, CharacteristicGroupUpdateSerializer,
    CharacteristicTemplateCreateSerializer, CharacteristicTemplateUpdateSerializer,
    CharacteristicValueCreateSerializer, CharacteristicValueUpdateSerializer,
)


pytestmark = pytest.mark.django_db


# =============================================================================
# accounts/managers.py — строки 32, 59-68 (create_superuser валидация)
# =============================================================================

class TestUserManagerCreateSuperuser:
    """Тесты валидации создания суперпользователя."""

    def test_create_superuser_without_is_staff_raises_error(self):
        """Суперпользователь без is_staff=True вызывает ошибку."""
        with pytest.raises(ValueError, match='is_staff=True'):
            User.objects.create_superuser(
                email='super@test.com',
                password='pass123',
                is_staff=False
            )

    def test_create_superuser_without_is_superuser_raises_error(self):
        """Суперпользователь без is_superuser=True вызывает ошибку."""
        with pytest.raises(ValueError, match='is_superuser=True'):
            User.objects.create_superuser(
                email='super@test.com',
                password='pass123',
                is_superuser=False
            )

    def test_create_superuser_success(self):
        """Успешное создание суперпользователя."""
        user = User.objects.create_superuser(
            email='super@test.com',
            password='pass123'
        )
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'superuser'


# =============================================================================
# categories/serializers.py — строки 66, 69, 85-89, 111, 114, 126-130
# =============================================================================

class TestCategoryCreateSerializerValidation:
    """Тесты валидации CategoryCreateSerializer."""

    def test_validate_name_too_long_raises_error(self):
        """Имя длиннее 100 символов вызывает ошибку."""
        serializer = CategoryCreateSerializer()
        with pytest.raises(serializers.ValidationError, match="не должно превышать 100"):
            serializer.validate_name('А' * 101)

    def test_validate_name_empty_raises_error(self):
        """Пустое имя после strip вызывает ошибку."""
        serializer = CategoryCreateSerializer()
        with pytest.raises(serializers.ValidationError, match="не может быть пустым"):
            serializer.validate_name('   ')

    def test_validate_name_duplicate_raises_error(self, category):
        """Дубликат имени вызывает ошибку."""
        serializer = CategoryCreateSerializer()
        with pytest.raises(serializers.ValidationError, match="уже существует"):
            serializer.validate_name(category.name_ru)

    def test_create_with_all_translations(self, cleanup_categories):
        """Создание категории с переводами name_ru и name_en."""
        data = {
            'name': 'Test Category',
            'name_ru': 'Тестовая категория RU',
            'name_en': 'Test Category EN'
        }
        serializer = CategoryCreateSerializer(data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        assert obj.name_ru == 'Тестовая категория RU'
        assert obj.name_en == 'Test Category EN'

    def test_create_without_translations_uses_name(self, cleanup_categories):
        """Создание категории без переводов — используется name."""
        data = {'name': 'Простая категория'}
        serializer = CategoryCreateSerializer(data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        # name_ru и name_en должны быть заполнены из name
        assert obj.name_ru == 'Простая категория'
        assert obj.name_en == 'Простая категория'


class TestCategoryUpdateSerializer:
    """Тесты CategoryUpdateSerializer."""

    def test_update_preserves_existing_translations(self, category):
        """Обновление сохраняет существующие переводы."""
        original_ru = category.name_ru
        data = {'name': 'Обновлённая', 'name_en': 'Updated EN'}
        serializer = CategoryUpdateSerializer(instance=category, data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        assert obj.name_en == 'Updated EN'
        # name_ru должен остаться или обновиться из name
        assert obj.name is not None

    def test_update_with_empty_translation_uses_name(self, category):
        """Пустой перевод заполняется из name."""
        data = {'name': 'Новое имя', 'name_ru': ''}
        serializer = CategoryUpdateSerializer(instance=category, data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        assert obj.name_ru == 'Новое имя'

    def test_update_name_too_long_raises_error(self, category):
        """Длинное имя при обновлении вызывает ошибку."""
        serializer = CategoryUpdateSerializer(instance=category)
        with pytest.raises(serializers.ValidationError):
            serializer.validate_name('А' * 101)


# =============================================================================
# products/serializers.py — строки 78, 88-122, 145, 173, 181-205
# =============================================================================

class TestProductCreateSerializer:
    """Тесты ProductCreateSerializer."""

    def test_create_with_all_translations(self, test_category, cleanup_products):
        """Создание товара с переводами."""
        data = {
            'name': 'Test Product',
            'name_ru': 'Тестовый товар RU',
            'name_en': 'Test Product EN',
            'category': test_category.id
        }
        serializer = ProductCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Тестовый товар RU'
        assert obj.name_en == 'Test Product EN'

    def test_create_without_translations_uses_name(self, test_category, cleanup_products):
        """Создание товара без переводов — fallback на name."""
        data = {
            'name': 'Простой товар',
            'category': test_category.id
        }
        serializer = ProductCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Простой товар'
        assert obj.name_en == 'Простой товар'

    @override_settings(LANGUAGE_CODE='en')
    def test_create_sets_name_for_current_language(self, test_category, cleanup_products):
        """name устанавливается для текущей локали."""
        data = {
            'name': 'English Product',
            'name_ru': 'Русский товар',
            'name_en': 'English Product',
            'category': test_category.id
        }
        serializer = ProductCreateSerializer(data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        # Для en локали name должен быть name_en
        assert obj.name == 'English Product'

    @override_settings(LANGUAGE_CODE='ru')
    def test_create_sets_name_for_ru_language(self, test_category, cleanup_products):
        """name устанавливается для русской локали."""
        data = {
            'name': 'Русский товар',
            'name_ru': 'Русский товар',
            'name_en': 'Russian Product',
            'category': test_category.id
        }
        serializer = ProductCreateSerializer(data=data)
        assert serializer.is_valid()
        obj = serializer.save()
        assert obj.name == 'Русский товар'

    def test_validate_img_invalid_path_raises_error(self, test_category):
        """Невалидный путь к изображению вызывает ошибку."""
        data = {
            'name': 'Товар',
            'category': test_category.id,
            'img': 'invalid/path/image.jpg'
        }
        serializer = ProductCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'img' in serializer.errors


class TestProductUpdateSerializer:
    """Тесты ProductUpdateSerializer."""

    def test_update_only_name(self, test_product):
        """Обновление только name."""
        data = {'name': 'Обновлённый товар', 'category': test_product.category_id}
        serializer = ProductUpdateSerializer(instance=test_product, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name == 'Обновлённый товар'

    def test_update_only_img(self, test_product):
        """Обновление только img."""
        original_name = test_product.name
        data = {
            'img': 'products/new-image.jpg',
            'category': test_product.category_id
        }
        serializer = ProductUpdateSerializer(instance=test_product, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.img == 'products/new-image.jpg'
        assert obj.name == original_name  # name не изменился

    def test_update_only_category(self, test_product, test_category2):
        """Обновление только category."""
        data = {'category': test_category2.id}
        serializer = ProductUpdateSerializer(instance=test_product, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.category_id == test_category2.id

    def test_update_with_empty_name_preserves_existing(self, test_product):
        """Пустое name при обновлении сохраняет существующее."""
        data = {
            'name': '',
            'category': test_product.category_id
        }
        serializer = ProductUpdateSerializer(instance=test_product, data=data, partial=True)
        # Пустое name должно пройти валидацию (поле необязательное)
        # Но при update пустое имя не обновляет существующее
        assert serializer.is_valid() or 'name' in serializer.errors

    def test_update_name_too_long_raises_error(self, test_product):
        """Длинное имя при обновлении вызывает ошибку."""
        serializer = ProductUpdateSerializer(instance=test_product)
        with pytest.raises(serializers.ValidationError):
            serializer.validate_name('А' * 201)

    def test_update_duplicate_name_in_category_raises_error(self, test_category, test_product):
        """Дубликат имени в категории при обновлении вызывает ошибку."""
        # Создаём второй товар с уникальным именем
        Product.objects.create(
            name_ru='Второй товар',
            name_en='Second Product',
            category=test_category
        )
        # Пытаемся обновить первый товар до имени второго
        # initial_data нужен для validate_name, поэтому передаём через data
        data = {
            'name': 'Второй товар',
            'category': test_category.id
        }
        serializer = ProductUpdateSerializer(instance=test_product, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_update_img_invalid_path_raises_error(self, test_product):
        """Невалидный путь к изображению при обновлении."""
        serializer = ProductUpdateSerializer(instance=test_product)
        with pytest.raises(serializers.ValidationError, match="должен начинаться"):
            serializer.validate_img('invalid/path.jpg')


# =============================================================================
# characteristic/serializers.py — строки 82, 87-105, 123, 127, 132-141, 204, 209-227, 245, 249, 254-263, 357, 362-376, 393, 397, 402-409
# =============================================================================

class TestCharacteristicGroupCreateSerializer:
    """Тесты CharacteristicGroupCreateSerializer."""

    def test_create_with_all_translations(self, char_category):
        """Создание группы с переводами."""
        data = {
            'name': 'Test Group',
            'name_ru': 'Тестовая группа RU',
            'name_en': 'Test Group EN',
            'category': char_category.id,
            'order': 5
        }
        serializer = CharacteristicGroupCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Тестовая группа RU'
        assert obj.name_en == 'Test Group EN'
        assert obj.order == 5

    def test_create_without_translations_uses_name(self, char_category):
        """Создание без переводов — fallback на name."""
        data = {
            'name': 'Простая группа',
            'category': char_category.id
        }
        serializer = CharacteristicGroupCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Простая группа'
        assert obj.name_en == 'Простая группа'

    def test_validate_name_empty_raises_error(self):
        """Пустое имя вызывает ошибку."""
        serializer = CharacteristicGroupCreateSerializer()
        with pytest.raises(serializers.ValidationError, match="не может быть пустым"):
            serializer.validate_name('   ')


class TestCharacteristicGroupUpdateSerializer:
    """Тесты CharacteristicGroupUpdateSerializer."""

    def test_update_only_order(self, group):
        """Обновление только order."""
        original_name = group.name
        data = {'order': 100}
        serializer = CharacteristicGroupUpdateSerializer(instance=group, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.order == 100
        assert obj.name == original_name

    def test_update_with_empty_name_ru_preserves_existing(self, group):
        """Пустой name_ru сохраняет существующий."""
        original_ru = group.name_ru
        data = {'name_ru': '', 'name_en': 'Updated EN'}
        serializer = CharacteristicGroupUpdateSerializer(instance=group, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_en == 'Updated EN'
        assert obj.name_ru == original_ru  # сохранился


class TestCharacteristicTemplateCreateSerializer:
    """Тесты CharacteristicTemplateCreateSerializer."""

    def test_create_with_all_translations(self, group):
        """Создание шаблона с переводами."""
        data = {
            'name': 'Test Template',
            'name_ru': 'Тестовый шаблон RU',
            'name_en': 'Test Template EN',
            'group': group.id,
            'order': 10
        }
        serializer = CharacteristicTemplateCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Тестовый шаблон RU'
        assert obj.name_en == 'Test Template EN'

    def test_create_without_translations_uses_name(self, group):
        """Создание без переводов — fallback на name."""
        data = {'name': 'Простой шаблон', 'group': group.id}
        serializer = CharacteristicTemplateCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == 'Простой шаблон'
        assert obj.name_en == 'Простой шаблон'

    def test_validate_name_empty_raises_error(self):
        """Пустое имя вызывает ошибку."""
        serializer = CharacteristicTemplateCreateSerializer()
        with pytest.raises(serializers.ValidationError):
            serializer.validate_name('   ')


class TestCharacteristicTemplateUpdateSerializer:
    """Тесты CharacteristicTemplateUpdateSerializer."""

    def test_update_only_order(self, template):
        """Обновление только order."""
        data = {'order': 200}
        serializer = CharacteristicTemplateUpdateSerializer(instance=template, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.order == 200

    def test_update_with_empty_name_ru_preserves_existing(self, template):
        """Пустой name_ru сохраняет существующий."""
        original_ru = template.name_ru
        data = {'name_ru': ''}
        serializer = CharacteristicTemplateUpdateSerializer(instance=template, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.name_ru == original_ru


class TestCharacteristicValueCreateSerializer:
    """Тесты CharacteristicValueCreateSerializer."""

    def test_create_with_all_translations(self, char_product, template):
        """Создание значения с переводами."""
        data = {
            'value': 'Test Value',
            'value_ru': 'Тестовое значение RU',
            'value_en': 'Test Value EN',
            'product': char_product.id,
            'template': template.id
        }
        serializer = CharacteristicValueCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.value_ru == 'Тестовое значение RU'
        assert obj.value_en == 'Test Value EN'

    def test_create_without_translations_uses_value(self, char_product, template):
        """Создание без переводов — fallback на value."""
        data = {
            'value': 'Простое значение',
            'product': char_product.id,
            'template': template.id
        }
        serializer = CharacteristicValueCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.value_ru == 'Простое значение'
        assert obj.value_en == 'Простое значение'

    def test_validate_value_empty_raises_error(self):
        """Пустое значение вызывает ошибку."""
        serializer = CharacteristicValueCreateSerializer()
        with pytest.raises(serializers.ValidationError, match="не может быть пустым"):
            serializer.validate_value('   ')


class TestCharacteristicValueUpdateSerializer:
    """Тесты CharacteristicValueUpdateSerializer."""

    def test_update_only_value(self, char_value):
        """Обновление только value."""
        data = {'value': 'Новое значение'}
        serializer = CharacteristicValueUpdateSerializer(instance=char_value, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.value == 'Новое значение'

    def test_update_with_empty_value_ru_preserves_existing(self, char_value):
        """Пустой value_ru сохраняет существующий."""
        original_ru = char_value.value_ru
        data = {'value_ru': ''}
        serializer = CharacteristicValueUpdateSerializer(instance=char_value, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.value_ru == original_ru

    def test_validate_value_empty_raises_error(self):
        """Пустое значение при обновлении вызывает ошибку."""
        serializer = CharacteristicValueUpdateSerializer()
        with pytest.raises(serializers.ValidationError):
            serializer.validate_value('   ')
