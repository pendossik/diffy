"""Интеграционные тесты для API категорий."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CategoryAPITestCase(TestCase):
    """Тесты API категорий."""

    def setUp(self):
        """Настройка тестов."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123',
            role='user'
        )

    def test_list_categories_unauthenticated(self):
        """Получение списка категорий без авторизации - успех."""
        response = self.client.get('/api/catalog/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_with_data(self):
        """Получение списка категорий с данными."""
        from catalog.models import Category
        Category.objects.create(name='Electronics')
        Category.objects.create(name='Clothing')

        response = self.client.get('/api/catalog/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_categories_with_search(self):
        """Поиск категорий."""
        from catalog.models import Category
        Category.objects.create(name='Electronics')
        Category.objects.create(name='Electronics Plus')
        Category.objects.create(name='Clothing')

        response = self.client.get('/api/catalog/categories/?search=electron')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_category_as_admin(self):
        """Создание категории администратором - успех."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Category'}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')

    def test_create_category_as_regular_user(self):
        """Создание категории обычным пользователем - отказ."""
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Category'}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_unauthenticated(self):
        """Создание категории без авторизации - отказ."""
        data = {'name': 'New Category'}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_empty_name(self):
        """Создание категории с пустым названием - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': ''}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_duplicate_name(self):
        """Создание категории с дублирующим названием - ошибка."""
        from catalog.models import Category
        Category.objects.create(name='Existing')
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Existing'}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_name_too_long(self):
        """Создание категории с названием более 100 символов - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'a' * 101}
        response = self.client.post('/api/catalog/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_category(self):
        """Получение категории по ID - успех."""
        from catalog.models import Category
        category = Category.objects.create(name='Test Category')
        response = self.client.get(f'/api/catalog/categories/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_retrieve_category_not_found(self):
        """Получение несуществующей категории - 404."""
        response = self.client.get('/api/catalog/categories/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_category_as_admin(self):
        """Обновление категории администратором - успех."""
        from catalog.models import Category
        category = Category.objects.create(name='Old Name')
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_update_category_as_regular_user(self):
        """Обновление категории обычным пользователем - отказ."""
        from catalog.models import Category
        category = Category.objects.create(name='Test')
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_not_found(self):
        """Обновление несуществующей категории - 404."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put('/api/catalog/categories/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_category_duplicate_name(self):
        """Обновление категории с дублирующим названием - ошибка."""
        from catalog.models import Category
        Category.objects.create(name='Existing')
        category = Category.objects.create(name='ToUpdate')
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Existing'}
        response = self.client.put(f'/api/catalog/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_category_as_admin(self):
        """Удаление категории администратором - успех."""
        from catalog.models import Category
        category = Category.objects.create(name='To Delete')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/catalog/categories/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_delete_category_as_regular_user(self):
        """Удаление категории обычным пользователем - отказ."""
        from catalog.models import Category
        category = Category.objects.create(name='To Delete')
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/catalog/categories/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_not_found(self):
        """Удаление несуществующей категории - 404."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/catalog/categories/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)