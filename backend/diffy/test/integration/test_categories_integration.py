"""Интеграционные тесты приложения categories."""
import pytest
from django.urls import reverse
from rest_framework import status
from categories.models import Category


pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class TestCategoriesFullWorkflow:
    """Полный сценарий работы с категориями."""
    
    def test_admin_full_crud_cycle(self, admin_client):
        """
        Интеграционный тест полного цикла: 
        создание → чтение → обновление → удаление.
        """
        # Create
        create_url = reverse('category-create')
        create_response = admin_client.post(create_url, {
            'name_ru': 'Интеграционная',
            'name_en': 'Integration'
        }, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        category_id = create_response.data['id']
        
        # Read (detail)
        detail_url = reverse('category-detail', kwargs={'category_id': category_id})
        read_response = admin_client.get(detail_url)
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.data['name_ru'] == 'Интеграционная'
        
        # Read (list)
        list_url = reverse('category-list')
        list_response = admin_client.get(list_url)
        assert list_response.status_code == status.HTTP_200_OK
        assert any(cat['id'] == category_id for cat in list_response.data['results'])
        
        # Update
        update_url = reverse('category-update', kwargs={'category_id': category_id})
        update_response = admin_client.patch(update_url, {
            'name_ru': 'Обновлённая интеграционная'
        }, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        
        # Verify update
        verify_response = admin_client.get(detail_url)
        assert verify_response.data['name_ru'] == 'Обновлённая интеграционная'
        
        # Delete
        delete_response = admin_client.delete(delete_url)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify deleted
        final_response = admin_client.get(detail_url)
        assert final_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_read_only_access(self, authenticated_client, categories_batch):
        """
        Обычный пользователь имеет только чтение.
        """
        # Can read list
        list_url = reverse('category-list')
        list_response = authenticated_client.get(list_url)
        assert list_response.status_code == status.HTTP_200_OK
        
        # Can read detail
        category = categories_batch[0]
        detail_url = reverse('category-detail', kwargs={'category_id': category.id})
        detail_response = authenticated_client.get(detail_url)
        assert detail_response.status_code == status.HTTP_200_OK
        
        # Cannot create
        create_url = reverse('category-create')
        create_response = authenticated_client.post(create_url, {'name_ru': 'Test'}, format='json')
        assert create_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Cannot update
        update_url = reverse('category-update', kwargs={'category_id': category.id})
        update_response = authenticated_client.patch(update_url, {'name_ru': 'Hacked'}, format='json')
        assert update_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Cannot delete
        delete_url = reverse('category-delete', kwargs={'category_id': category.id})
        delete_response = authenticated_client.delete(delete_url)
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN


class TestSearchIntegration:
    """Интеграционные тесты поиска."""
    
    def test_search_multilanguage(self, authenticated_client, categories_batch):
        """
        Поиск работает на обоих языках в реальном запросе.
        """
        url = reverse('category-list')
        
        # Поиск по-русски
        ru_response = authenticated_client.get(url, {'search': 'электрон'})
        assert ru_response.status_code == status.HTTP_200_OK
        assert ru_response.data['count'] >= 1
        
        # Поиск по-английски
        en_response = authenticated_client.get(url, {'search': 'phone'})
        assert en_response.status_code == status.HTTP_200_OK
        assert en_response.data['count'] >= 1
    
    def test_search_with_pagination(self, authenticated_client):
        """
        Поиск и пагинация работают вместе.
        """
        # Создаём много категорий с похожими именами
        for i in range(30):
            Category.objects.create(
                name_ru=f'Тест Категория {i}',
                name_en=f'Test Category {i}'
            )
        
        url = reverse('category-list')
        response = authenticated_client.get(url, {
            'search': 'тест',
            'page': 1,
            'page_size': 10
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 30  # Все найдены
        assert len(response.data['results']) == 10  # Но на странице только 10
        assert response.data['next'] is not None  # Есть следующая страница


class TestMultilanguageIntegration:
    """Интеграционные тесты мультиязычности."""
    
    def test_response_contains_both_languages(self, authenticated_client, category):
        """
        API возвращает оба языка независимо от Accept-Language.
        """
        url = reverse('category-detail', kwargs={'category_id': category.id})
        
        # Запрос с ru
        response_ru = authenticated_client.get(url, HTTP_ACCEPT_LANGUAGE='ru')
        assert response_ru.status_code == status.HTTP_200_OK
        assert response_ru.data['name_ru'] == category.name_ru
        assert response_ru.data['name_en'] == category.name_en
        
        # Запрос с en
        response_en = authenticated_client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        assert response_en.status_code == status.HTTP_200_OK
        assert response_en.data['name_ru'] == category.name_ru
        assert response_en.data['name_en'] == category.name_en
    
    def test_name_field_respects_accept_language(self, authenticated_client, category):
        """
        Поле 'name' меняется в зависимости от Accept-Language.
        """
        url = reverse('category-detail', kwargs={'category_id': category.id})
        
        response_ru = authenticated_client.get(url, HTTP_ACCEPT_LANGUAGE='ru')
        response_en = authenticated_client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        
        # Благодаря modeltranslation, name должен соответствовать языку
        assert response_ru.data['name'] == category.name_ru
        assert response_en.data['name'] == category.name_en