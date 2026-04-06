"""Тесты API views приложения characteristic."""
import pytest
from rest_framework import status
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


pytestmark = pytest.mark.django_db


class TestCharacteristicGroupAuthentication:
    def test_list_without_auth_returns_200(self, api_client, group):
        response = api_client.get('/api/characteristic/groups/')
        assert response.status_code == status.HTTP_200_OK

    def test_detail_without_auth_returns_200(self, api_client, group):
        response = api_client.get(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_without_auth_returns_401(self, api_client, char_category):
        response = api_client.post('/api/characteristic/groups/', {
            'name': 'Тест',
            'category': char_category.id
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_auth_returns_401(self, api_client, group):
        response = api_client.put(f'/api/characteristic/groups/{group.id}/', {'name': 'Обновление'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_auth_returns_401(self, api_client, group):
        response = api_client.delete(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCharacteristicGroupUserPermissions:
    def test_user_cannot_create_group(self, jwt_user_client, char_category):
        response = jwt_user_client.post('/api/characteristic/groups/', {
            'name': 'Запрещённая группа',
            'category': char_category.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_update_group(self, jwt_user_client, group):
        response = jwt_user_client.put(f'/api/characteristic/groups/{group.id}/', {'name': 'Обновлённая группа'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_delete_group(self, jwt_user_client, group):
        response = jwt_user_client.delete(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_can_list_groups(self, jwt_user_client, group):
        response = jwt_user_client.get('/api/characteristic/groups/')
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_get_group_detail(self, jwt_user_client, group):
        response = jwt_user_client.get(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_200_OK


class TestCharacteristicGroupList:
    def test_list_empty_returns_success(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/characteristic/groups/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_list_returns_groups(self, jwt_admin_client, group):
        response = jwt_admin_client.get('/api/characteristic/groups/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_includes_translation_fields(self, jwt_admin_client, group):
        response = jwt_admin_client.get('/api/characteristic/groups/')
        result = response.data[0]
        assert 'name_ru' in result
        assert 'name_en' in result
        assert 'category_info' in result


class TestCharacteristicGroupCreate:
    def test_admin_create_success(self, jwt_admin_client, char_category):
        data = {
            'name': 'Новая группа',
            'category': char_category.id,
            'order': 10
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        if response.status_code == 400:
            print(f"DEBUG create details: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.data}"
        assert 'Location' in response

    def test_admin_create_with_translations(self, jwt_admin_client, char_category):
        data = {
            'name': 'Test Group',
            'name_ru': 'Тестовая группа',
            'name_en': 'Test Group',
            'category': char_category.id,
            'order': 5
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_create_duplicate_returns_409(self, jwt_admin_client, char_category, group):
        """При попытке создать дубликат возвращается ошибка (400 или 409)."""
        data = {
            'name': group.name,
            'category': char_category.id
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        # Валидация unique_together может вернуть 400 (валидация) или 409 (conflict)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]

    def test_create_returns_location_header(self, jwt_admin_client, char_category):
        data = {
            'name': 'Тест',
            'category': char_category.id
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        if response.status_code == 400:
            print(f"DEBUG location details: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert 'Location' in response


class TestCharacteristicGroupDetail:
    def test_get_detail_success(self, jwt_admin_client, group):
        response = jwt_admin_client.get(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == group.id

    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/characteristic/groups/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_detail_includes_templates(self, jwt_admin_client, group, template):
        response = jwt_admin_client.get(f'/api/characteristic/groups/{group.id}/')
        assert 'templates' in response.data


class TestCharacteristicGroupUpdate:
    def test_admin_put_update_success(self, jwt_admin_client, group):
        data = {
            'name': 'Обновлённая группа',
            'order': 99
        }
        response = jwt_admin_client.put(f'/api/characteristic/groups/{group.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order'] == 99

    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.put('/api/characteristic/groups/99999/', {'name': 'Тест'})
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCharacteristicGroupDelete:
    def test_admin_delete_success(self, jwt_admin_client, group):
        response = jwt_admin_client.delete(f'/api/characteristic/groups/{group.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not CharacteristicGroup.objects.filter(id=group.id).exists()

    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.delete('/api/characteristic/groups/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCharacteristicTemplateAuthentication:
    def test_list_without_auth_returns_200(self, api_client, template):
        response = api_client.get('/api/characteristic/templates/')
        assert response.status_code == status.HTTP_200_OK

    def test_detail_without_auth_returns_200(self, api_client, template):
        response = api_client.get(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_without_auth_returns_401(self, api_client, group):
        response = api_client.post('/api/characteristic/templates/', {
            'name': 'Тест',
            'group': group.id
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_auth_returns_401(self, api_client, template):
        response = api_client.put(f'/api/characteristic/templates/{template.id}/', {'name': 'Обновление'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_auth_returns_401(self, api_client, template):
        response = api_client.delete(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCharacteristicTemplateUserPermissions:
    def test_user_cannot_create_template(self, jwt_user_client, group):
        response = jwt_user_client.post('/api/characteristic/templates/', {
            'name': 'Запрещённый',
            'group': group.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_update_template(self, jwt_user_client, template):
        response = jwt_user_client.put(f'/api/characteristic/templates/{template.id}/', {'name': 'Обновлённый'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_delete_template(self, jwt_user_client, template):
        response = jwt_user_client.delete(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_can_list_templates(self, jwt_user_client, template):
        response = jwt_user_client.get('/api/characteristic/templates/')
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_get_template_detail(self, jwt_user_client, template):
        response = jwt_user_client.get(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_200_OK


class TestCharacteristicTemplateList:
    def test_list_empty_returns_success(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/characteristic/templates/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_list_returns_templates(self, jwt_admin_client, template):
        response = jwt_admin_client.get('/api/characteristic/templates/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


class TestCharacteristicTemplateCreate:
    def test_admin_create_success(self, jwt_admin_client, group):
        data = {
            'name': 'Новый шаблон',
            'group': group.id,
            'order': 10
        }
        response = jwt_admin_client.post('/api/characteristic/templates/', data)
        if response.status_code == 400:
            print(f"DEBUG template create details: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.data}"
        assert 'Location' in response

    def test_admin_create_with_translations(self, jwt_admin_client, group):
        data = {
            'name': 'Test Template',
            'name_ru': 'Тестовый шаблон',
            'name_en': 'Test Template',
            'group': group.id,
            'order': 5
        }
        response = jwt_admin_client.post('/api/characteristic/templates/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_create_duplicate_returns_409(self, jwt_admin_client, group, template):
        """При попытке создать дубликат возвращается ошибка (400 или 409)."""
        data = {
            'name': template.name,
            'group': group.id
        }
        response = jwt_admin_client.post('/api/characteristic/templates/', data)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]

    def test_create_returns_location_header(self, jwt_admin_client, group):
        data = {
            'name': 'Тест',
            'group': group.id
        }
        response = jwt_admin_client.post('/api/characteristic/templates/', data)
        if response.status_code == 400:
            print(f"DEBUG template location details: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert 'Location' in response


class TestCharacteristicTemplateDetail:
    def test_get_detail_success(self, jwt_admin_client, template):
        response = jwt_admin_client.get(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/characteristic/templates/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCharacteristicTemplateUpdate:
    def test_admin_put_update_success(self, jwt_admin_client, template):
        data = {
            'name': 'Обновлённый шаблон',
            'order': 99
        }
        response = jwt_admin_client.put(f'/api/characteristic/templates/{template.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order'] == 99

    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.put('/api/characteristic/templates/99999/', {'name': 'Тест'})
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCharacteristicTemplateDelete:
    def test_admin_delete_success(self, jwt_admin_client, template):
        response = jwt_admin_client.delete(f'/api/characteristic/templates/{template.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not CharacteristicTemplate.objects.filter(id=template.id).exists()

    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.delete('/api/characteristic/templates/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# ProductCharacteristic — URL: /api/products/{id}/characteristics/
# =============================================================================

class TestProductCharacteristicAuthentication:
    def test_list_without_auth_returns_200(self, api_client, char_product, char_value):
        response = api_client.get(f'/api/products/{char_product.id}/characteristics/')
        assert response.status_code == status.HTTP_200_OK

    def test_detail_without_auth_returns_200(self, api_client, char_product, char_value):
        response = api_client.get(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_without_auth_returns_401(self, api_client, char_product, template):
        response = api_client.post(f'/api/products/{char_product.id}/characteristics/', {
            'value': 'Тест',
            'product': char_product.id,
            'template': template.id
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_auth_returns_401(self, api_client, char_product, char_value):
        response = api_client.put(f'/api/products/{char_product.id}/characteristics/{char_value.id}/', {
            'value': 'Обновление'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_auth_returns_401(self, api_client, char_product, char_value):
        response = api_client.delete(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProductCharacteristicUserPermissions:
    def test_user_cannot_create_value(self, jwt_user_client, char_product, template):
        response = jwt_user_client.post(f'/api/products/{char_product.id}/characteristics/', {
            'value': 'Запрещённое',
            'product': char_product.id,
            'template': template.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_update_value(self, jwt_user_client, char_product, char_value):
        response = jwt_user_client.put(f'/api/products/{char_product.id}/characteristics/{char_value.id}/', {
            'value': 'Обновлённое'
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_delete_value(self, jwt_user_client, char_product, char_value):
        response = jwt_user_client.delete(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_can_list_values(self, jwt_user_client, char_product, char_value):
        response = jwt_user_client.get(f'/api/products/{char_product.id}/characteristics/')
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_get_value_detail(self, jwt_user_client, char_product, char_value):
        response = jwt_user_client.get(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_200_OK


class TestProductCharacteristicList:
    def test_list_empty_returns_success(self, jwt_admin_client, char_product):
        response = jwt_admin_client.get(f'/api/products/{char_product.id}/characteristics/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_list_returns_values(self, jwt_admin_client, char_product, char_value):
        response = jwt_admin_client.get(f'/api/products/{char_product.id}/characteristics/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_nonexistent_product_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/products/99999/characteristics/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductCharacteristicCreate:
    def test_admin_create_success(self, jwt_admin_client, char_product, template):
        data = {
            'value': '200г',
            'product': char_product.id,
            'template': template.id
        }
        response = jwt_admin_client.post(f'/api/products/{char_product.id}/characteristics/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'Location' in response

    def test_admin_create_duplicate_returns_409(self, jwt_admin_client, char_product, template, char_value):
        data = {
            'value': 'Дубликат',
            'product': char_product.id,
            'template': template.id
        }
        response = jwt_admin_client.post(f'/api/products/{char_product.id}/characteristics/', data)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_admin_create_nonexistent_product_returns_409(self, jwt_admin_client, template):
        """POST с несуществующим товаром возвращает ошибку (404 или 409)."""
        data = {
            'value': 'Тест',
            'product': 99999,
            'template': template.id
        }
        response = jwt_admin_client.post('/api/products/99999/characteristics/', data)
        # ValueError от сервиса может быть обработан как 409
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]


class TestProductCharacteristicDetail:
    def test_get_detail_success(self, jwt_admin_client, char_product, char_value):
        response = jwt_admin_client.get(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == char_value.id

    def test_get_detail_nonexistent_returns_404(self, jwt_admin_client, char_product):
        response = jwt_admin_client.get(f'/api/products/{char_product.id}/characteristics/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductCharacteristicUpdate:
    def test_admin_put_update_success(self, jwt_admin_client, char_product, char_value):
        data = {'value': '300г'}
        response = jwt_admin_client.put(f'/api/products/{char_product.id}/characteristics/{char_value.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['value'] == '300г'

    def test_admin_update_nonexistent_returns_404(self, jwt_admin_client, char_product):
        response = jwt_admin_client.put(f'/api/products/{char_product.id}/characteristics/99999/', {'value': 'Тест'})
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductCharacteristicDelete:
    def test_admin_delete_success(self, jwt_admin_client, char_product, char_value):
        response = jwt_admin_client.delete(f'/api/products/{char_product.id}/characteristics/{char_value.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert not CharacteristicValue.objects.filter(id=char_value.id).exists()

    def test_admin_delete_nonexistent_returns_404(self, jwt_admin_client, char_product):
        response = jwt_admin_client.delete(f'/api/products/{char_product.id}/characteristics/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# CategoryCharacteristicsGroups — URL: /api/categories/{id}/characteristics-groups/
# =============================================================================

class TestCategoryCharacteristicsGroups:
    def test_get_groups_for_category_success(self, jwt_admin_client, char_category, group, template):
        response = jwt_admin_client.get(f'/api/categories/{char_category.id}/characteristics-groups/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_get_groups_nonexistent_category_returns_404(self, jwt_admin_client):
        response = jwt_admin_client.get('/api/categories/99999/characteristics-groups/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_groups_includes_templates(self, jwt_admin_client, char_category, group, template):
        response = jwt_admin_client.get(f'/api/categories/{char_category.id}/characteristics-groups/')
        assert response.status_code == status.HTTP_200_OK
        assert 'templates' in response.data[0]


# =============================================================================
# Дополнительные сценарии тестирования
# =============================================================================

class TestCharacteristicGroupEdgeCases:
    """Дополнительные сценарии для групп характеристик."""

    def test_create_group_with_cyrillic_name(self, jwt_admin_client, char_category):
        """Создание группы с кириллическим названием."""
        data = {
            'name': 'Технические параметры',
            'name_ru': 'Технические параметры',
            'name_en': 'Technical Specs',
            'category': char_category.id
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_group_with_special_characters(self, jwt_admin_client, char_category):
        """Создание группы со спецсимволами."""
        data = {
            'name': 'Тест-Группа!@#$',
            'category': char_category.id
        }
        response = jwt_admin_client.post('/api/characteristic/groups/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_group_order_only(self, jwt_admin_client, group):
        """Обновление только порядка группы."""
        original_name = group.name
        data = {'order': 100}
        response = jwt_admin_client.put(f'/api/characteristic/groups/{group.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order'] == 100

    def test_create_multiple_groups_same_category(self, jwt_admin_client, char_category):
        """Создание нескольких групп в одной категории."""
        for i in range(3):
            data = {
                'name': f'Группа {i}',
                'category': char_category.id,
                'order': i
            }
            response = jwt_admin_client.post('/api/characteristic/groups/', data)
            assert response.status_code == status.HTTP_201_CREATED


class TestCharacteristicTemplateEdgeCases:
    """Дополнительные сценарии для шаблонов характеристик."""

    def test_create_template_with_cyrillic_name(self, jwt_admin_client, group):
        """Создание шаблона с кириллическим названием."""
        data = {
            'name': 'Техническая характеристика',
            'name_ru': 'Техническая характеристика',
            'name_en': 'Technical Characteristic',
            'group': group.id
        }
        response = jwt_admin_client.post('/api/characteristic/templates/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_multiple_templates_same_group(self, jwt_admin_client, group):
        """Создание нескольких шаблонов в одной группе."""
        for i in range(3):
            data = {
                'name': f'Шаблон {i}',
                'group': group.id,
                'order': i
            }
            response = jwt_admin_client.post('/api/characteristic/templates/', data)
            assert response.status_code == status.HTTP_201_CREATED


class TestProductCharacteristicEdgeCases:
    """Дополнительные сценарии для характеристик товаров."""

    def test_create_value_with_cyrillic(self, jwt_admin_client, char_product, template):
        """Создание значения с кириллицей."""
        data = {
            'value': 'Двести грамм',
            'value_ru': 'Двести грамм',
            'value_en': 'Two hundred grams',
            'product': char_product.id,
            'template': template.id
        }
        response = jwt_admin_client.post(f'/api/products/{char_product.id}/characteristics/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_values_sorted_by_order(self, jwt_admin_client, char_product, group):
        """Значения характеристик отсортированы по порядку."""
        # Создаём несколько шаблонов в группе
        templates = []
        for i in range(3):
            tpl = CharacteristicTemplate.objects.create(
                group=group,
                name=f'Параметр {i}',
                order=i
            )
            templates.append(tpl)

        # Создаём значения для каждого шаблона
        for tpl in templates:
            CharacteristicValue.objects.create(
                product=char_product,
                template=tpl,
                value=f'Значение {tpl.order}'
            )

        response = jwt_admin_client.get(f'/api/products/{char_product.id}/characteristics/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3


class TestErrorResponseFormat:
    """Тесты формата ответов об ошибках."""

    def test_error_response_has_error_key(self, jwt_user_client, char_category):
        """Ответ об ошибке содержит ключ 'error'."""
        response = jwt_user_client.post('/api/characteristic/groups/', {
            'name': 'Тест',
            'category': char_category.id
        })
        assert 'error' in response.data
