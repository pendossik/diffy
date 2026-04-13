"""Юнит-тесты для сервисов приложения comparisons."""
import pytest
from unittest.mock import patch, MagicMock
from comparisons.services import (
    FavoriteComparisonService,
    ComparisonCharacteristicsService,
)
from comparisons.models import FavoriteComparison
from products.models import Product
from categories.models import Category
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def admin_user(db):
    """Администратор."""
    from accounts.models import User
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        username='admin_user',
        role='admin',
        is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Обычный пользователь."""
    from accounts.models import User
    return User.objects.create_user(
        email='user@test.com',
        password='testpass123',
        username='regular_user',
        role='user'
    )


@pytest.fixture
def category(db):
    """Тестовая категория."""
    return Category.objects.create(
        name_ru='Электроника',
        name_en='Electronics'
    )


@pytest.fixture
def products(db, category):
    """Создаёт 3 товара."""
    return [
        Product.objects.create(
            name_ru=f'Товар {i}',
            name_en=f'Product {i}',
            category=category
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def comparison(db, admin_user, products):
    """Избранное сравнение."""
    comp = FavoriteComparison.objects.create(
        user=admin_user,
        products_hash='1,2,3'
    )
    comp.products.set(products)
    return comp


# =============================================================================
# ТЕСТЫ: FavoriteComparisonService._generate_products_hash
# =============================================================================

class TestGenerateProductsHash:
    """Тесты генерации хеша набора товаров."""

    def test_same_ids_same_hash(self):
        """[1,2,3] и [3,2,1] должны иметь одинаковый хеш."""
        hash1 = FavoriteComparisonService._generate_products_hash([1, 2, 3])
        hash2 = FavoriteComparisonService._generate_products_hash([3, 2, 1])
        assert hash1 == hash2
        assert hash1 == '1,2,3'

    def test_different_ids_different_hash(self):
        """Разные наборы должны иметь разные хеши."""
        hash1 = FavoriteComparisonService._generate_products_hash([1, 2])
        hash2 = FavoriteComparisonService._generate_products_hash([1, 3])
        assert hash1 != hash2

    def test_single_element_hash(self):
        """Хеш для одного элемента."""
        result = FavoriteComparisonService._generate_products_hash([5])
        assert result == '5'

    def test_hash_is_string(self):
        """Хеш должен быть строкой."""
        result = FavoriteComparisonService._generate_products_hash([3, 1, 2])
        assert isinstance(result, str)


# =============================================================================
# ТЕСТЫ: FavoriteComparisonService - READ
# =============================================================================

@pytest.mark.django_db
class TestFavoriteComparisonServiceRead:
    """Тесты чтения избранных сравнений."""

    def test_get_user_comparisons_returns_queryset(self, admin_user, comparison):
        result = FavoriteComparisonService.get_user_comparisons(admin_user)
        assert list(result) == [comparison]

    def test_get_user_comparisons_empty(self, admin_user):
        result = FavoriteComparisonService.get_user_comparisons(admin_user)
        assert list(result) == []

    def test_get_user_comparisons_only_own(self, admin_user, regular_user, comparison):
        """Пользователь видит только свои сравнения."""
        result = FavoriteComparisonService.get_user_comparisons(regular_user)
        assert list(result) == []

    def test_get_comparison_detail_success(self, admin_user, comparison):
        result = FavoriteComparisonService.get_comparison_detail(admin_user, comparison.id)
        assert result.id == comparison.id
        assert result.user == admin_user

    def test_get_comparison_detail_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Сравнение не найдено"):
            FavoriteComparisonService.get_comparison_detail(admin_user, 99999)

    def test_get_comparison_detail_wrong_user(self, admin_user, regular_user, comparison):
        """Пользователь не может чужое сравнение."""
        with pytest.raises(ValueError, match="нет доступа"):
            FavoriteComparisonService.get_comparison_detail(regular_user, comparison.id)


# =============================================================================
# ТЕСТЫ: FavoriteComparisonService - ADD
# =============================================================================

@pytest.mark.django_db
class TestFavoriteComparisonServiceAdd:
    """Тесты добавления в избранное."""

    def test_add_to_favorites_success(self, admin_user, products):
        product_ids = [p.id for p in products]
        result = FavoriteComparisonService.add_to_favorites(
            user=admin_user,
            product_ids=product_ids
        )
        assert result.user == admin_user
        assert result.products.count() == 3
        assert result.products_hash is not None

    def test_add_to_favorites_order_independent(self, admin_user, products):
        """Порядок товаров не влияет на хеш."""
        ids1 = [products[0].id, products[1].id, products[2].id]
        ids2 = [products[2].id, products[1].id, products[0].id]

        comp1 = FavoriteComparisonService.add_to_favorites(admin_user, ids1)

        with pytest.raises(ValueError, match="уже есть в избранных"):
            FavoriteComparisonService.add_to_favorites(admin_user, ids2)

    def test_add_to_favorites_duplicate_same_user(self, admin_user, products, comparison):
        """Дубликат сравнения для одного пользователя."""
        product_ids = [p.id for p in products]
        # fixture comparison уже использует products с hash='1,2,3'
        # Но реальные product.id != 1,2,3, поэтому хеши не совпадают
        # Пересоздадим comparison с правильным hash
        comparison.delete()
        real_hash = FavoriteComparisonService._generate_products_hash(product_ids)
        comp = FavoriteComparison.objects.create(
            user=admin_user,
            products_hash=real_hash
        )
        comp.products.set(products)

        with pytest.raises(ValueError, match="уже есть в избранных"):
            FavoriteComparisonService.add_to_favorites(
                user=admin_user,
                product_ids=product_ids
            )

    def test_add_to_favorites_different_users(self, admin_user, regular_user, products, category):
        """Разные пользователи могут создавать одинаковые сравнения."""
        product_ids = [p.id for p in products]
        real_hash = FavoriteComparisonService._generate_products_hash(product_ids)

        # Admin создаёт сравнение
        comp1 = FavoriteComparison.objects.create(
            user=admin_user,
            products_hash=real_hash
        )
        comp1.products.set(products)

        # Создаём ещё одного пользователя и другие товары
        from accounts.models import User
        other_user = User.objects.create_user(
            email='other@test.com',
            password='pass123',
            username='other_user',
            role='user'
        )
        other_products = [
            Product.objects.create(
                name_ru=f'Другой товар {i}',
                name_en=f'Other Product {i}',
                category=category
            )
            for i in range(10, 13)
        ]
        other_product_ids = [p.id for p in other_products]

        # other_user может создать сравнение со своими товарами
        result = FavoriteComparisonService.add_to_favorites(other_user, other_product_ids)
        assert result.user == other_user

    def test_add_to_favorites_less_than_two(self, admin_user, products):
        """Меньше 2 товаров — ошибка."""
        with pytest.raises(ValueError, match="минимум 2"):
            FavoriteComparisonService.add_to_favorites(
                user=admin_user,
                product_ids=[products[0].id]
            )

    def test_add_to_favorites_empty_list(self, admin_user):
        """Пустой список — ошибка."""
        with pytest.raises(ValueError, match="минимум 2"):
            FavoriteComparisonService.add_to_favorites(
                user=admin_user,
                product_ids=[]
            )

    def test_add_to_favorites_nonexistent_product(self, admin_user):
        """Несуществующий товар — ошибка."""
        with pytest.raises(ValueError):
            FavoriteComparisonService.add_to_favorites(
                user=admin_user,
                product_ids=[99999, 99998]
            )

    def test_different_users_same_products_no_integrity_error(self, admin_user, regular_user, products):
        """
        CR-3: Разные пользователи могут создавать одинаковые наборы товаров.
        Раньше products_hash unique=True вызывал IntegrityError.
        """
        product_ids = [p.id for p in products]

        # Пользователь 1 создаёт сравнение
        comp1 = FavoriteComparisonService.add_to_favorites(admin_user, product_ids)

        # Пользователь 2 создаёт такое же сравнение — должно работать
        comp2 = FavoriteComparisonService.add_to_favorites(regular_user, product_ids)

        assert comp1.products_hash == comp2.products_hash
        assert comp1.user != comp2.user
        assert comp1.id != comp2.id

    def test_different_users_same_products_logs_warning(self, admin_user, regular_user, products, caplog):
        """
        CR-3: При попытке добавить дубликат для того же пользователя — warning в логе.
        """
        import logging
        logger = logging.getLogger('comparisons')
        logger.setLevel(logging.WARNING)

        product_ids = [p.id for p in products]
        FavoriteComparisonService.add_to_favorites(regular_user, product_ids)

        with pytest.raises(ValueError, match="уже есть в избранных"):
            FavoriteComparisonService.add_to_favorites(regular_user, product_ids)

        assert "дубликат" in caplog.text.lower()
        assert regular_user.email in caplog.text


# =============================================================================
# ТЕСТЫ: FavoriteComparisonService - REMOVE
# =============================================================================

@pytest.mark.django_db
class TestFavoriteComparisonServiceRemove:
    """Тесты удаления из избранного."""

    def test_remove_from_favorites_success(self, admin_user, comparison):
        result = FavoriteComparisonService.remove_from_favorites(
            user=admin_user,
            comparison_id=comparison.id
        )
        assert result is True
        assert not FavoriteComparison.objects.filter(id=comparison.id).exists()

    def test_remove_from_favorites_not_found(self, admin_user):
        with pytest.raises(ValueError, match="Сравнение не найдено"):
            FavoriteComparisonService.remove_from_favorites(
                user=admin_user,
                comparison_id=99999
            )

    def test_remove_from_favorites_wrong_user(self, admin_user, regular_user, comparison):
        """Пользователь не может удалить чужое сравнение."""
        with pytest.raises(ValueError, match="нет доступа"):
            FavoriteComparisonService.remove_from_favorites(
                user=regular_user,
                comparison_id=comparison.id
            )


# =============================================================================
# ТЕСТЫ: ComparisonCharacteristicsService
# =============================================================================

@pytest.mark.django_db
class TestComparisonCharacteristicsService:
    """Тесты сравнения товаров по характеристикам."""

    def test_compare_products_success(self, products, category):
        """Успешное сравнение товаров."""
        group = CharacteristicGroup.objects.create(
            category=category,
            name_ru='Основные',
            name_en='Basic',
            order=0
        )
        template = CharacteristicTemplate.objects.create(
            group=group,
            name_ru='Процессор',
            name_en='Processor',
            order=0
        )

        # Создаём значения
        for product in products[:2]:
            CharacteristicValue.objects.create(
                product=product,
                template=template,
                value=f'CPU для {product.name_ru}',
                value_ru=f'CPU для {product.name_ru}',
                value_en=f'CPU for {product.name_en}'
            )

        product_ids = [products[0].id, products[1].id]
        result = ComparisonCharacteristicsService.compare_products_by_characteristics(
            product_ids=product_ids
        )

        assert result['products_count'] == 2
        assert len(result['products']) == 2
        assert len(result['groups']) == 1
        assert 'characteristics' in result['groups'][0]

    def test_compare_products_less_than_two(self):
        """Меньше 2 товаров — ошибка."""
        with pytest.raises(ValueError, match="минимум 2"):
            ComparisonCharacteristicsService.compare_products_by_characteristics(
                product_ids=[1]
            )

    def test_compare_products_empty_list(self):
        """Пустой список — ошибка."""
        with pytest.raises(ValueError, match="минимум 2"):
            ComparisonCharacteristicsService.compare_products_by_characteristics(
                product_ids=[]
            )

    def test_compare_products_nonexistent(self):
        """Несуществующие товары — ошибка."""
        with pytest.raises(ValueError):
            ComparisonCharacteristicsService.compare_products_by_characteristics(
                product_ids=[99999, 99998]
            )

    def test_compare_products_without_characteristics(self, products):
        """Сравнение товаров без характеристик."""
        product_ids = [products[0].id, products[1].id]
        result = ComparisonCharacteristicsService.compare_products_by_characteristics(
            product_ids=product_ids
        )

        assert result['products_count'] == 2
        assert len(result['groups']) == 0

    def test_compare_products_includes_translations(self, products, category):
        """Результат содержит переводы."""
        group = CharacteristicGroup.objects.create(
            category=category,
            name_ru='Основные',
            name_en='Basic',
            order=0
        )
        template = CharacteristicTemplate.objects.create(
            group=group,
            name_ru='Процессор',
            name_en='Processor',
            order=0
        )

        for product in products[:2]:
            CharacteristicValue.objects.create(
                product=product,
                template=template,
                value='Intel i7',
                value_ru='Intel i7',
                value_en='Intel i7'
            )

        product_ids = [products[0].id, products[1].id]
        result = ComparisonCharacteristicsService.compare_products_by_characteristics(
            product_ids=product_ids
        )

        group_data = result['groups'][0]
        assert 'group_name_ru' in group_data
        assert 'group_name_en' in group_data

        char_data = group_data['characteristics'][0]
        assert 'template_name_ru' in char_data
        assert 'template_name_en' in char_data

    def test_compare_products_values_include_translations(self, products, category):
        """Значения характеристик содержат переводы."""
        group = CharacteristicGroup.objects.create(
            category=category,
            name_ru='Основные',
            order=0
        )
        template = CharacteristicTemplate.objects.create(
            group=group,
            name_ru='Процессор',
            order=0
        )

        for product in products[:2]:
            CharacteristicValue.objects.create(
                product=product,
                template=template,
                value='CPU',
                value_ru='Процессор RU',
                value_en='CPU EN'
            )

        product_ids = [products[0].id, products[1].id]
        result = ComparisonCharacteristicsService.compare_products_by_characteristics(
            product_ids=product_ids
        )

        char_values = result['groups'][0]['characteristics'][0]['values']
        for product_id, val_data in char_values.items():
            assert 'value' in val_data
            assert 'value_ru' in val_data
            assert 'value_en' in val_data


# =============================================================================
# ТЕСТЫ: ЛОГИРОВАНИЕ
# =============================================================================

@pytest.mark.django_db
class TestComparisonServicesLogging:
    """Тесты проверки логирования операций."""

    @patch('comparisons.services.logger')
    def test_add_to_favorites_logs_info(self, mock_logger, admin_user, products):
        product_ids = [p.id for p in products]
        FavoriteComparisonService.add_to_favorites(
            user=admin_user,
            product_ids=product_ids
        )
        mock_logger.info.assert_called_once()
        assert 'избранное' in mock_logger.info.call_args[0][0].lower()

    @patch('comparisons.services.logger')
    def test_remove_from_favorites_logs_info(self, mock_logger, admin_user, comparison):
        FavoriteComparisonService.remove_from_favorites(
            user=admin_user,
            comparison_id=comparison.id
        )
        mock_logger.info.assert_called_once()
        assert 'удалено' in mock_logger.info.call_args[0][0].lower()
