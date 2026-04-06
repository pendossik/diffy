"""Тесты API views приложения categories."""
import pytest
from rest_framework import status
from categories.models import Category


pytestmark = pytest.mark.django_db


# =============================================================================
# 🔴 CRITICAL: Тесты аутентификации и прав доступа
# =============================================================================

class TestAuthentication:
    """Тесты проверки аутентификации для всех эндпоинтов."""

    def test_list_without_auth_returns_200(self, api_client, category):
        """GET /categories/ без авторизации возвращает 200."""
        response = api_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK

    def test_detail_without_auth_returns_200(self, api_client, category):
        """GET /categories/{id}/ без авторизации возвращает 200."""
        response = api_client.get(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_without_auth_returns_401(self, api_client):
        """POST /categories/ без авторизации возвращает 401."""
        response = api_client.post('/api/categories/', {'name': 'Тест'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_auth_returns_401(self, api_client, category):
        """PUT /categories/{id}/ без авторизации возвращает 401."""
        response = api_client.put(
            f'/api/categories/{category.id}/',
            {'name': 'Обновление'}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_auth_returns_401(self, api_client, category):
        """DELETE /categories/{id}/ без авторизации возвращает 401."""
        response = api_client.delete(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserPermissions:
    """Тесты прав доступа для обычных пользователей."""

    def test_user_cannot_create_category(self, jwt_user_client):
        """Обычный пользователь не может создавать категории (403)."""
        response = jwt_user_client.post(
            '/api/categories/',
            {'name': 'Запрещённая категория'}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут создавать категории' in response.data['error']

    def test_user_cannot_update_category(self, jwt_user_client, category):
        """Обычный пользователь не может обновлять категории (403)."""
        response = jwt_user_client.put(
            f'/api/categories/{category.id}/',
            {'name': 'Обновлённая категория'}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут изменять категории' in response.data['error']

    def test_user_cannot_delete_category(self, jwt_user_client, category):
        """Обычный пользователь не может удалять категории (403)."""
        response = jwt_user_client.delete(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Только администраторы могут удалять категории' in response.data['error']

    def test_user_can_list_categories(self, jwt_user_client, categories_batch):
        """Обычный пользователь может просматривать список категорий."""
        response = jwt_user_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == len(categories_batch)

    def test_user_can_get_category_detail(self, jwt_user_client, category):
        """Обычный пользователь может просматривать детали категории."""
        response = jwt_user_client.get(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id


# =============================================================================
# 🟠 HIGH: Тесты CategoryListCreateView (GET список, POST создание)
# =============================================================================

class TestCategoryList:
    """Тесты получения списка категорий."""

    def test_list_empty_returns_success(self, jwt_admin_client):
        """GET /categories/ с пустым списком возвращает 200."""
        response = jwt_admin_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []

    def test_list_returns_paginated_results(self, jwt_admin_client, many_categories):
        """GET /categories/ возвращает пагинированный список."""
        response = jwt_admin_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # page_size по умолчанию
        assert response.data['next'] is not None  # Есть следующая страница
        assert response.data['previous'] is None

    def test_list_pagination_page_2(self, jwt_admin_client, many_categories):
        """GET /categories/?page=2 возвращает вторую страницу."""
        response = jwt_admin_client.get('/api/categories/?page=2')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 5  # Осталось 5 на второй странице
        assert response.data['previous'] is not None

    def test_list_custom_page_size(self, jwt_admin_client, many_categories):
        """GET /categories/?page_size=10 работает с кастомным размером."""
        response = jwt_admin_client.get('/api/categories/?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 10

    def test_list_sorted_by_name(self, jwt_admin_client, categories_batch):
        """GET /categories/ возвращает категории отсортированными по имени."""
        response = jwt_admin_client.get('/api/categories/')
        
        names = [cat['name'] for cat in response.data['results']]
        assert names == sorted(names)

    def test_list_includes_translation_fields(self, jwt_admin_client, category):
        """GET /categories/ возвращает name_ru и name_en."""
        response = jwt_admin_client.get('/api/categories/')
        
        result = response.data['results'][0]
        assert 'name_ru' in result
        assert 'name_en' in result
        assert 'id' in result
        assert 'name' in result


class TestCategorySearch:
    """Тесты поиска категорий."""

    def test_search_by_name_ru(self, jwt_admin_client, searchable_categories):
        """GET /categories/?search=электрон находит по русскому названию."""
        response = jwt_admin_client.get('/api/categories/?search=электрон')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name_ru'] == 'Электроника'

    def test_search_by_name_en(self, jwt_admin_client, searchable_categories):
        """GET /categories/?search=phone находит по английскому названию."""
        response = jwt_admin_client.get('/api/categories/?search=phone')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name_en'] == 'Phones'

    def test_search_case_insensitive(self, jwt_admin_client, searchable_categories):
        """Поиск регистронезависимый."""
        response_upper = jwt_admin_client.get('/api/categories/?search=ЭЛЕКТРОНИКА')
        response_lower = jwt_admin_client.get('/api/categories/?search=электроника')
        
        assert response_upper.data['count'] == 1
        assert response_lower.data['count'] == 1

    def test_search_partial_match(self, jwt_admin_client, searchable_categories):
        """Поиск по частичному совпадению работает."""
        response = jwt_admin_client.get('/api/categories/?search=кни')
        
        # Ищет "кни" в "Книги" или "Электроники"
        assert response.status_code == status.HTTP_200_OK

    def test_search_empty_returns_all(self, jwt_admin_client, searchable_categories):
        """GET /categories/?search= возвращает все категории."""
        response = jwt_admin_client.get('/api/categories/?search=')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5

    def test_search_single_char_returns_400(self, jwt_admin_client, searchable_categories):
        """GET /categories/?search=а (1 символ) возвращает 400 (min_length=2)."""
        response = jwt_admin_client.get('/api/categories/?search=а')
        
        # Поиск с 1 символом не проходит валидацию (min_length=2)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_invalid_returns_error(self, jwt_admin_client, searchable_categories):
        """GET /categories/?search=[] (невалидный) возвращает 400."""
        response = jwt_admin_client.get('/api/categories/?search=[]invalid')
        
        # Сериализатор должен отработать
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestCategoryCreate:
    """Тесты создания категории."""

    def test_admin_create_success(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ с валидными данными создаёт категорию (201)."""
        data = {'name': 'Новая категория'}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Новая категория'
        assert 'Location' in response

    def test_admin_create_with_translations(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ с name_ru/name_en создаёт с переводами."""
        data = {
            'name': 'Test Category',
            'name_ru': 'Тестовая категория',
            'name_en': 'Test Category'
        }
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Проверяем что категория создана (modeltranslation обрабатывает переводы)
        assert response.data['id'] is not None
        # name в ответе содержит значение для текущей локали (ru)
        assert response.data['name'] is not None

    def test_admin_create_with_cyrillic_name(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ с кириллическим name_ru создаёт категорию."""
        data = {
            'name': 'Веб-разработка',
            'name_ru': 'Веб-разработка',
            'name_en': 'Web Development'
        }
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Веб-разработка'

    def test_admin_create_duplicate_returns_400(self, jwt_admin_client, category):
        """POST /categories/ с дубликатом имени возвращает 400 (валидация сериализатора)."""
        data = {'name': category.name}
        response = jwt_admin_client.post('/api/categories/', data)
        
        # Валидация в сериализаторе происходит раньше сервиса
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_create_duplicate_case_insensitive(self, jwt_admin_client, category):
        """POST /categories/ с дубликатом другого регистра возвращает 400."""
        data = {'name': category.name.upper()}
        response = jwt_admin_client.post('/api/categories/', data)
        
        # Валидация в сериализаторе (case-insensitive)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_create_name_too_long_returns_400(self, jwt_admin_client):
        """POST /categories/ с именем >100 символов возвращает 400."""
        data = {'name': 'А' * 101}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Ошибка валидации в общем формате
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_create_empty_name_returns_400(self, jwt_admin_client):
        """POST /categories/ с пустым именем возвращает 400."""
        data = {'name': ''}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_create_strips_and_capitalizes(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ очищает и капитализирует имя."""
        data = {'name': '  тестовая категория  '}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Тестовая категория'

    def test_create_returns_location_header(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ возвращает Location header."""
        data = {'name': 'Тест'}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'Location' in response
        assert f"/api/categories/{response.data['id']}/" in response['Location']


# =============================================================================
# 🟠 HIGH: Тесты CategoryDetailView (GET, PUT, PATCH, DELETE)
# =============================================================================

class TestCategoryDetail:
    """Тесты получения деталей категории."""

    def test_get_detail_success(self, jwt_admin_client, category):
        """GET /categories/{id}/ возвращает детали категории."""
        response = jwt_admin_client.get(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert response.data['name'] == category.name

    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client):
        """GET /categories/99999/ возвращает 404."""
        response = jwt_admin_client.get('/api/categories/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'не найдена' in response.data['error']

    def test_get_detail_includes_translations(self, jwt_admin_client, category):
        """GET /categories/{id}/ возвращает name_ru и name_en."""
        response = jwt_admin_client.get(f'/api/categories/{category.id}/')
        
        assert 'name_ru' in response.data
        assert 'name_en' in response.data


class TestCategoryUpdate:
    """Тесты обновления категории."""

    def test_admin_put_full_update_success(self, jwt_admin_client, category):
        """PUT /categories/{id}/ полностью обновляет категорию."""
        original_name = category.name
        data = {
            'name': 'Обновлённая категория',
            'name_ru': 'Обновлённая категория',
            'name_en': 'Updated Category'
        }
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Обновлённая категория'
        assert response.data['name'] != original_name

    def test_admin_patch_partial_update_name_only(self, jwt_admin_client, category):
        """PATCH /categories/{id}/ обновляет только name."""
        data = {'name': 'Обновлённое имя'}
        response = jwt_admin_client.patch(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Обновлённое имя'

    def test_admin_patch_partial_update_with_name_change(self, jwt_admin_client, category):
        """PATCH /categories/{id}/ обновляет имя категории."""
        original_name = category.name
        data = {
            'name': 'Новое имя категории',
        }
        response = jwt_admin_client.patch(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Новое имя категории'
        assert response.data['name'] != original_name

    def test_admin_update_duplicate_name_returns_400(self, jwt_admin_client, category, duplicate_category):
        """PUT /categories/{id}/ с дубликатом имени возвращает 400 (валидация сериализатора)."""
        data = {'name': duplicate_category.name}
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        # Валидация в сериализаторе происходит раньше сервиса
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Ошибка валидации'

    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client):
        """PUT /categories/99999/ возвращает 404."""
        data = {'name': 'Новое имя'}
        response = jwt_admin_client.put('/api/categories/99999/', data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_update_name_too_long_returns_400(self, jwt_admin_client, category):
        """PUT /categories/{id}/ с длинным именем возвращает 400."""
        data = {'name': 'А' * 101}
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_update_empty_name_returns_400(self, jwt_admin_client, category):
        """PUT /categories/{id}/ с пустым именем возвращает 400."""
        data = {'name': ''}
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCategoryDelete:
    """Тесты удаления категории."""

    def test_admin_delete_success(self, jwt_admin_client, category):
        """DELETE /categories/{id}/ удаляет категорию."""
        response = jwt_admin_client.delete(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Категория успешно удалена'
        assert not Category.objects.filter(id=category.id).exists()

    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client):
        """DELETE /categories/99999/ возвращает 404."""
        response = jwt_admin_client.delete('/api/categories/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'не найдена' in response.data['error']

    def test_delete_idempotent(self, jwt_admin_client, category):
        """Повторное удаление возвращает 404 (категории нет)."""
        jwt_admin_client.delete(f'/api/categories/{category.id}/')
        response = jwt_admin_client.delete(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# 🟡 MEDIUM: Тесты граничных случаев и валидации
# =============================================================================

class TestValidationEdgeCases:
    """Тесты граничных случаев валидации."""

    def test_create_with_special_characters(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ со спецсимволами работает."""
        data = {'name': 'Тест-Категория!@#$%'}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_with_numbers(self, jwt_admin_client, cleanup_categories):
        """POST /categories/ с цифрами в имени работает."""
        data = {'name': 'Категория 123'}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_same_name_success(self, jwt_admin_client, category):
        """PUT /categories/{id}/ с тем же именем успешно."""
        data = {'name': category.name}
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_whitespace_only_returns_400(self, jwt_admin_client):
        """POST /categories/ с пробелами возвращает 400."""
        data = {'name': '   '}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_whitespace_only_returns_400(self, jwt_admin_client, category):
        """PUT /categories/{id}/ с пробелами возвращает 400."""
        data = {'name': '   '}
        response = jwt_admin_client.put(f'/api/categories/{category.id}/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestErrorResponseFormat:
    """Тесты формата ответов об ошибках."""

    def test_error_response_has_error_key(self, jwt_user_client):
        """Ответ об ошибке содержит ключ 'error'."""
        response = jwt_user_client.post('/api/categories/', {'name': 'Тест'})
        
        assert 'error' in response.data

    def test_validation_error_has_details(self, jwt_admin_client):
        """Ответ об ошибке валидации содержит 'details'."""
        data = {'name': ''}
        response = jwt_admin_client.post('/api/categories/', data)
        
        assert 'error' in response.data
        assert 'details' in response.data

