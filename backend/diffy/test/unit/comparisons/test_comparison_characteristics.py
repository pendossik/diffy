"""Тесты для сравнения товаров по характеристикам."""
import pytest
from rest_framework import status
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue
from products.models import Product
from categories.models import Category


pytestmark = pytest.mark.django_db


class TestComparisonCharacteristicsView:
    """Тесты для эндпоинта сравнения товаров по характеристикам."""

    def test_compare_two_laptops_success(self, jwt_admin_client):
        """Успешное сравнение двух ноутбуков."""
        # Создаём категорию
        category = Category.objects.create(
            name_ru='Ноутбуки',
            name_en='Laptops'
        )

        # Создаём товары
        laptop1 = Product.objects.create(
            name_ru='Dell XPS 15',
            name_en='Dell XPS 15',
            category=category
        )
        laptop2 = Product.objects.create(
            name_ru='MacBook Pro 16',
            name_en='MacBook Pro 16',
            category=category
        )

        # Создаём группу характеристик
        group = CharacteristicGroup.objects.create(
            category=category,
            name_ru='Основные',
            name_en='Basic',
            order=0
        )

        # Создаём шаблоны
        cpu_template = CharacteristicTemplate.objects.create(
            group=group,
            name_ru='Процессор',
            name_en='Processor',
            order=0
        )
        ram_template = CharacteristicTemplate.objects.create(
            group=group,
            name_ru='Оперативная память',
            name_en='RAM',
            order=1
        )

        # Создаём значения для первого ноутбука
        CharacteristicValue.objects.create(
            product=laptop1,
            template=cpu_template,
            value='Intel Core i7',
            value_ru='Intel Core i7',
            value_en='Intel Core i7'
        )
        CharacteristicValue.objects.create(
            product=laptop1,
            template=ram_template,
            value='16 ГБ',
            value_ru='16 ГБ',
            value_en='16 GB'
        )

        # Создаём значения для второго ноутбука
        CharacteristicValue.objects.create(
            product=laptop2,
            template=cpu_template,
            value='Apple M2',
            value_ru='Apple M2',
            value_en='Apple M2'
        )
        CharacteristicValue.objects.create(
            product=laptop2,
            template=ram_template,
            value='32 ГБ',
            value_ru='32 ГБ',
            value_en='32 GB'
        )

        # Запрос на сравнение
        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [laptop1.id, laptop2.id]}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['products_count'] == 2
        assert len(response.data['products']) == 2
        assert len(response.data['groups']) > 0

    def test_compare_same_product_returns_error(self, jwt_admin_client):
        """Попытка сравнить товар с самим собой должна вернуть ошибку."""
        category = Category.objects.create(name_ru='Ноутбуки')
        product = Product.objects.create(
            name_ru='Dell XPS 15',
            category=category
        )

        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [product.id, product.id]}
        )

        # Ожидается ошибка (товары дублируются)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Ошибка может быть "не найдены" так как один товар считается дважды
        assert 'ошибка' in response.data.get('error', '').lower() or 'не найдены' in response.data.get('error', '').lower()

    def test_compare_single_product_returns_error(self, jwt_admin_client):
        """Попытка сравнить один товар должна вернуть ошибку."""
        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [1]}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'минимум 2' in response.data['error'].lower()

    def test_compare_nonexistent_products_returns_error(self, jwt_admin_client):
        """Попытка сравнить несуществующие товары должна вернуть ошибку."""
        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [99999, 99998]}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'не найдены' in response.data['error'].lower()

    def test_compare_products_from_different_categories(self, jwt_admin_client):
        """Успешное сравнение товаров из разных категорий."""
        # Создаём категории
        laptops_category = Category.objects.create(
            name_ru='Ноутбуки',
            name_en='Laptops'
        )
        tablets_category = Category.objects.create(
            name_ru='Планшеты',
            name_en='Tablets'
        )

        # Создаём товары
        laptop = Product.objects.create(
            name_ru='Dell XPS 15',
            name_en='Dell XPS 15',
            category=laptops_category
        )
        tablet = Product.objects.create(
            name_ru='iPad Pro',
            name_en='iPad Pro',
            category=tablets_category
        )

        # Запрос на сравнение
        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [laptop.id, tablet.id]}
        )

        # Должно вернуть успех (даже если характеристики разные)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['products_count'] == 2

    def test_compare_with_one_product_missing_returns_error(self, jwt_admin_client):
        """Попытка сравнить товары когда один не существует."""
        category = Category.objects.create(name_ru='Ноутбуки')
        product = Product.objects.create(
            name_ru='Dell XPS 15',
            category=category
        )

        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [product.id, 99999]}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'не найдены' in response.data['error'].lower()

    def test_compare_without_product_ids_returns_error(self, jwt_admin_client):
        """Запрос без product_ids должен вернуть ошибку."""
        response = jwt_admin_client.get('/api/comparisons/characteristics/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Требуется параметр product_ids' in response.data['error']

    def test_compare_with_invalid_product_ids_format(self, jwt_admin_client):
        """Запрос с неверным форматом product_ids."""
        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': ['abc', 'def']}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'неверный формат' in response.data['error'].lower()

    def test_compare_returns_translations(self, jwt_admin_client):
        """Сравнение должно возвращать переводы названий групп и характеристик."""
        category = Category.objects.create(
            name_ru='Ноутбуки',
            name_en='Laptops'
        )

        product1 = Product.objects.create(
            name_ru='Dell XPS 15',
            name_en='Dell XPS 15',
            category=category
        )
        product2 = Product.objects.create(
            name_ru='MacBook Pro',
            name_en='MacBook Pro',
            category=category
        )

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

        CharacteristicValue.objects.create(
            product=product1,
            template=template,
            value='Intel Core i7',
            value_ru='Intel Core i7',
            value_en='Intel Core i7'
        )

        response = jwt_admin_client.get(
            '/api/comparisons/characteristics/',
            {'product_ids': [product1.id, product2.id]}
        )

        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем наличие переводов
        group_data = response.data['groups'][0]
        assert 'group_name_ru' in group_data
        assert 'group_name_en' in group_data
        
        char_data = group_data['characteristics'][0]
        assert 'template_name_ru' in char_data
        assert 'template_name_en' in char_data
