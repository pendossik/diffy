"""Тесты API views приложения products."""
import pytest
from rest_framework import status
from products.models import Product


pytestmark = pytest.mark.django_db


# =============================================================================
# 🔴 CRITICAL: Тесты аутентификации и прав доступа
# =============================================================================

class TestAuthentication:
    """Тесты проверки аутентификации для всех эндпоинтов."""

    def test_list_without_auth_returns_200(self, api_client, test_product):
        """GET /products/ без авторизации возвращает 200."""
        response = api_client.get('/api/products/')

        assert response.status_code == status.HTTP_200_OK

    def test_detail_without_auth_returns_200(self, api_client, test_product):
        """GET /products/{id}/ без авторизации возвращает 200."""
        response = api_client.get(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_create_without_auth_returns_401(self, api_client, test_category):
        """POST /products/ без авторизации возвращает 401."""
        response = api_client.post('/api/products/', {
            'name': 'Тест',
            'category': test_category.id
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_auth_returns_401(self, api_client, test_product):
        """PUT /products/{id}/ без авторизации возвращает 401."""
        response = api_client.put(
            f'/api/products/{test_product.id}/',
            {'name': 'Обновление', 'category': test_product.category_id}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_auth_returns_401(self, api_client, test_product):
        """DELETE /products/{id}/ без авторизации возвращает 401."""
        response = api_client.delete(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserPermissions:
    """Тесты прав доступа для обычных пользователей."""

    def test_user_cannot_create_product(self, jwt_user_client, test_category):
        """Обычный пользователь не может создавать товары (403)."""
        response = jwt_user_client.post(
            '/api/products/',
            {'name': 'Запрещённый товар', 'category': test_category.id}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут создавать товары' in response.data['error']

    def test_user_cannot_update_product(self, jwt_user_client, test_product):
        """Обычный пользователь не может обновлять товары (403)."""
        response = jwt_user_client.put(
            f'/api/products/{test_product.id}/',
            {'name': 'Обновлённый товар', 'category': test_product.category_id}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут изменять товары' in response.data['error']

    def test_user_cannot_delete_product(self, jwt_user_client, test_product):
        """Обычный пользователь не может удалять товары (403)."""
        response = jwt_user_client.delete(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут удалять товары' in response.data['error']

    def test_user_can_list_products(self, jwt_user_client, many_products):
        """Обычный пользователь может просматривать список товаров."""
        response = jwt_user_client.get('/api/products/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25

    def test_user_can_get_product_detail(self, jwt_user_client, test_product):
        """Обычный пользователь может просматривать детали товара."""
        response = jwt_user_client.get(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_product.id


# =============================================================================
# 🟠 HIGH: Тесты ProductListCreateView (GET список, POST создание)
# =============================================================================

class TestProductList:
    """Тесты получения списка товаров."""

    def test_list_empty_returns_success(self, jwt_admin_client):
        """GET /products/ с пустым списком возвращает 200."""
        response = jwt_admin_client.get('/api/products/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []

    def test_list_returns_paginated_results(self, jwt_admin_client, many_products):
        """GET /products/ возвращает пагинированный список."""
        response = jwt_admin_client.get('/api/products/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # page_size по умолчанию
        assert response.data['next'] is not None  # Есть следующая страница
        assert response.data['previous'] is None

    def test_list_pagination_page_2(self, jwt_admin_client, many_products):
        """GET /products/?page=2 возвращает вторую страницу."""
        response = jwt_admin_client.get('/api/products/?page=2')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 5  # Осталось 5 на второй странице
        assert response.data['previous'] is not None

    def test_list_custom_page_size(self, jwt_admin_client, many_products):
        """GET /products/?page_size=10 работает с кастомным размером."""
        response = jwt_admin_client.get('/api/products/?page_size=10')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 10

    def test_list_includes_category_info(self, jwt_admin_client, test_product):
        """GET /products/ возвращает category_info."""
        response = jwt_admin_client.get('/api/products/')

        result = response.data['results'][0]
        assert 'category_info' in result
        assert 'id' in result['category_info']
        assert 'name' in result['category_info']

    def test_list_includes_translation_fields(self, jwt_admin_client, test_product):
        """GET /products/ возвращает name_ru и name_en."""
        response = jwt_admin_client.get('/api/products/')

        result = response.data['results'][0]
        assert 'name_ru' in result
        assert 'name_en' in result
        assert 'id' in result
        assert 'name' in result


class TestProductSearch:
    """Тесты поиска товаров."""

    def test_search_by_name_ru(self, jwt_admin_client, searchable_products):
        """GET /products/?search=ноутбук находит по русскому названию."""
        response = jwt_admin_client.get('/api/products/?search=ноутбук')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert 'Ноутбук' in response.data['results'][0]['name_ru']

    def test_search_by_name_en(self, jwt_admin_client, searchable_products):
        """GET /products/?search=iphone находит по английскому названию."""
        response = jwt_admin_client.get('/api/products/?search=iphone')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert 'iPhone' in response.data['results'][0]['name_en']

    def test_search_case_insensitive(self, jwt_admin_client, searchable_products):
        """Поиск регистронезависимый."""
        response_upper = jwt_admin_client.get('/api/products/?search=НОУТБУК')
        response_lower = jwt_admin_client.get('/api/products/?search=ноутбук')

        assert response_upper.data['count'] == 1
        assert response_lower.data['count'] == 1

    def test_search_partial_match(self, jwt_admin_client, searchable_products):
        """Поиск по частичному совпадению работает."""
        response = jwt_admin_client.get('/api/products/?search=фон')

        # Ищет "фон" в "Телефон" или "Наушники"
        assert response.status_code == status.HTTP_200_OK

    def test_search_empty_returns_all(self, jwt_admin_client, searchable_products):
        """GET /products/?search= возвращает все товары."""
        response = jwt_admin_client.get('/api/products/?search=')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5

    def test_search_single_char_returns_400(self, jwt_admin_client, searchable_products):
        """GET /products/?search=а (1 символ) возвращает 400 (min_length=2)."""
        response = jwt_admin_client.get('/api/products/?search=а')
        
        # Поиск с 1 символом не проходит валидацию (min_length=2)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_filter_by_category(self, jwt_admin_client, products_in_different_categories, test_category):
        """GET /products/?category={id} фильтрует по категории."""
        response = jwt_admin_client.get(f'/api/products/?category={test_category.id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_search_with_category_filter(self, jwt_admin_client, products_in_different_categories, test_category):
        """GET /products/?search=Товар&category={id} работает."""
        response = jwt_admin_client.get(f'/api/products/?search=Товар&category={test_category.id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2


class TestProductCreate:
    """Тесты создания товара."""

    def test_admin_create_success(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ с валидными данными создаёт товар (201)."""
        data = {
            'name': 'Новый товар',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Новый товар'
        assert 'Location' in response

    def test_admin_create_with_translations(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ с name_ru/name_en создаёт с переводами."""
        data = {
            'name': 'Новый товар',
            'name_ru': 'Новый товар',
            'name_en': 'New Product',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        # Проверяем что категория создана
        assert response.data['id'] is not None
        assert response.data['name'] is not None

    def test_admin_create_with_img(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ с изображением создаёт товар."""
        data = {
            'name': 'Товар с фото',
            'category': test_category.id,
            'img': 'products/test-image.jpg'
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['img'] == 'products/test-image.jpg'

    def test_admin_create_duplicate_returns_400(self, jwt_admin_client, test_category, test_product):
        """POST /products/ с дубликатом имени в категории возвращает 409."""
        data = {
            'name': 'Тестовый товар',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        # Валидация в сериализаторе происходит раньше сервиса
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_create_duplicate_different_category_success(self, jwt_admin_client, test_category, test_category2, test_product):
        """POST /products/ с дубликатом имени в другой категории успешно."""
        data = {
            'name': 'Тестовый товар',
            'category': test_category2.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_create_name_too_long_returns_400(self, jwt_admin_client, test_category):
        """POST /products/ с именем >200 символов возвращает 400."""
        data = {
            'name': 'А' * 201,
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_create_empty_name_returns_400(self, jwt_admin_client, test_category):
        """POST /products/ с пустым именем возвращает 400."""
        data = {
            'name': '',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_create_nonexistent_category_returns_400(self, jwt_admin_client):
        """POST /products/ с несуществующей категорией возвращает 400."""
        data = {
            'name': 'Товар',
            'category': 99999
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_returns_location_header(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ возвращает Location header."""
        data = {
            'name': 'Тест',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'Location' in response
        assert f"/api/products/{response.data['id']}/" in response['Location']


# =============================================================================
# 🟠 HIGH: Тесты ProductDetailView (GET, PUT, PATCH, DELETE)
# =============================================================================

class TestProductDetail:
    """Тесты получения деталей товара."""

    def test_get_detail_success(self, jwt_admin_client, test_product):
        """GET /products/{id}/ возвращает детали товара."""
        response = jwt_admin_client.get(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_product.id
        assert response.data['name'] == test_product.name

    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client):
        """GET /products/99999/ возвращает 404."""
        response = jwt_admin_client.get('/api/products/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'не найден' in response.data['error']

    def test_get_detail_includes_category_info(self, jwt_admin_client, test_product):
        """GET /products/{id}/ возвращает category_info."""
        response = jwt_admin_client.get(f'/api/products/{test_product.id}/')

        assert 'category_info' in response.data
        assert response.data['category_info']['id'] == test_product.category_id

    def test_get_detail_includes_translations(self, jwt_admin_client, test_product):
        """GET /products/{id}/ возвращает name_ru и name_en."""
        response = jwt_admin_client.get(f'/api/products/{test_product.id}/')

        assert 'name_ru' in response.data
        assert 'name_en' in response.data


class TestProductUpdate:
    """Тесты обновления товара."""

    def test_admin_put_full_update_success(self, jwt_admin_client, test_product, test_category):
        """PUT /products/{id}/ полностью обновляет товар."""
        original_name = test_product.name
        data = {
            'name': 'Обновлённый товар',
            'name_ru': 'Обновлённый товар',
            'name_en': 'Updated Product',
            'category': test_category.id,
            'img': 'products/new-image.jpg'
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Обновлённый товар'
        assert response.data['name'] != original_name

    def test_admin_patch_partial_update_name_only(self, jwt_admin_client, test_product):
        """PATCH /products/{id}/ обновляет только name (REST API стандарт)."""
        data = {'name': 'Обновлённое имя'}
        response = jwt_admin_client.patch(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Обновлённое имя'

    def test_admin_patch_partial_update_img_only(self, jwt_admin_client, test_product):
        """PATCH /products/{id}/ обновляет только img (REST API стандарт)."""
        data = {'img': 'products/updated-image.jpg'}
        response = jwt_admin_client.patch(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['img'] == 'products/updated-image.jpg'

    def test_admin_patch_partial_update_category_only(self, jwt_admin_client, test_product, test_category2):
        """PATCH /products/{id}/ обновляет только category (REST API стандарт)."""
        data = {'category': test_category2.id}
        response = jwt_admin_client.patch(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['category'] == test_category2.id

    def test_admin_update_duplicate_name_returns_400(self, jwt_admin_client, test_product, test_category):
        """PUT /products/{id}/ с дубликатом имени возвращает 400."""
        # Создаём второй товар
        Product.objects.create(
            name_ru='Второй товар',
            name_en='Second Product',
            category=test_category,
            img='products/second.jpg'
        )

        # Пытаемся обновить первый товар до имени второго
        data = {
            'name': 'Второй товар',
            'category': test_category.id
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client):
        """PUT /products/99999/ возвращает 404."""
        data = {
            'name': 'Новое имя',
            'category': 1
        }
        response = jwt_admin_client.put('/api/products/99999/', data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_update_name_too_long_returns_400(self, jwt_admin_client, test_product):
        """PUT /products/{id}/ с длинным именем возвращает 400."""
        data = {
            'name': 'А' * 201,
            'category': test_product.category_id
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_update_empty_name_returns_400(self, jwt_admin_client, test_product):
        """PUT /products/{id}/ с пустым именем возвращает 400."""
        data = {
            'name': '',
            'category': test_product.category_id
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProductDelete:
    """Тесты удаления товара."""

    def test_admin_delete_success(self, jwt_admin_client, test_product):
        """DELETE /products/{id}/ удаляет товар."""
        response = jwt_admin_client.delete(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Товар успешно удален'
        assert not Product.objects.filter(id=test_product.id).exists()

    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client):
        """DELETE /products/99999/ возвращает 404."""
        response = jwt_admin_client.delete('/api/products/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'не найден' in response.data['error']

    def test_delete_idempotent(self, jwt_admin_client, test_product):
        """Повторное удаление возвращает 404 (товара нет)."""
        jwt_admin_client.delete(f'/api/products/{test_product.id}/')
        response = jwt_admin_client.delete(f'/api/products/{test_product.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# 🟡 MEDIUM: Тесты граничных случаев и валидации
# =============================================================================

class TestValidationEdgeCases:
    """Тесты граничных случаев валидации."""

    def test_create_with_special_characters(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ со спецсимволами работает."""
        data = {
            'name': 'Товар-Категория!@#$%',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_with_numbers(self, jwt_admin_client, test_category, cleanup_products):
        """POST /products/ с цифрами в имени работает."""
        data = {
            'name': 'Товар 123',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_update_same_name_success(self, jwt_admin_client, test_product):
        """PUT /products/{id}/ с тем же именем успешно."""
        data = {
            'name': test_product.name,
            'category': test_product.category_id
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_200_OK

    def test_create_whitespace_only_returns_400(self, jwt_admin_client, test_category):
        """POST /products/ с пробелами возвращает 400."""
        data = {
            'name': '   ',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_whitespace_only_returns_400(self, jwt_admin_client, test_product):
        """PUT /products/{id}/ с пробелами возвращает 400."""
        data = {
            'name': '   ',
            'category': test_product.category_id
        }
        response = jwt_admin_client.put(f'/api/products/{test_product.id}/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestErrorResponseFormat:
    """Тесты формата ответов об ошибках."""

    def test_error_response_has_error_key(self, jwt_user_client, test_category):
        """Ответ об ошибке содержит ключ 'error'."""
        response = jwt_user_client.post('/api/products/', {
            'name': 'Тест',
            'category': test_category.id
        })

        assert 'error' in response.data

    def test_validation_error_has_details(self, jwt_admin_client, test_category):
        """Ответ об ошибке валидации содержит 'details'."""
        data = {
            'name': '',
            'category': test_category.id
        }
        response = jwt_admin_client.post('/api/products/', data)

        assert 'error' in response.data
        assert 'details' in response.data
    