"""Интеграционные тесты для API групп характеристик."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CharacteristicGroupAPITestCase(TestCase):
    """Тесты API групп характеристик."""

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
        from catalog.models import Category
        self.category = Category.objects.create(name='Test Category')

    def test_list_groups_unauthenticated(self):
        """Получение списка групп без авторизации - успех."""
        response = self.client.get('/api/catalog/characteristic-groups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_groups_with_data(self):
        """Получение списка групп с данными."""
        from catalog.models import CharacteristicGroup
        CharacteristicGroup.objects.create(name='Specs', category=self.category)
        CharacteristicGroup.objects.create(name='Dimensions', category=self.category)

        response = self.client.get('/api/catalog/characteristic-groups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_group_as_admin(self):
        """Создание группы администратором - успех."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Group', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/characteristic-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Group')

    def test_create_group_as_regular_user(self):
        """Создание группы обычным пользователем - отказ."""
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Group', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/characteristic-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group_invalid_category(self):
        """Создание группы с несуществующей категорией - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Group', 'category_id': 999}
        response = self.client.post('/api/catalog/characteristic-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_group_empty_name(self):
        """Создание группы с пустым названием - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': '', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/characteristic-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_group_name_too_long(self):
        """Создание группы с названием более 100 символов - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'a' * 101, 'category_id': self.category.id}
        response = self.client.post('/api/catalog/characteristic-groups/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_group(self):
        """Получение группы по ID - успех."""
        from catalog.models import CharacteristicGroup
        group = CharacteristicGroup.objects.create(name='Test Group', category=self.category)
        response = self.client.get(f'/api/catalog/characteristic-groups/{group.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Group')

    def test_retrieve_group_not_found(self):
        """Получение несуществующей группы - 404."""
        response = self.client.get('/api/catalog/characteristic-groups/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_group_as_admin(self):
        """Обновление группы администратором - успех."""
        from catalog.models import CharacteristicGroup
        group = CharacteristicGroup.objects.create(name='Old Name', category=self.category)
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/characteristic-groups/{group.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_update_group_as_regular_user(self):
        """Обновление группы обычным пользователем - отказ."""
        from catalog.models import CharacteristicGroup
        group = CharacteristicGroup.objects.create(name='Test', category=self.category)
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/characteristic-groups/{group.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_group_not_found(self):
        """Обновление несуществующей группы - 404."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put('/api/catalog/characteristic-groups/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_group_as_admin(self):
        """Удаление группы администратором - успех."""
        from catalog.models import CharacteristicGroup
        group = CharacteristicGroup.objects.create(name='To Delete', category=self.category)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/catalog/characteristic-groups/{group.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CharacteristicGroup.objects.filter(id=group.id).exists())

    def test_delete_group_as_regular_user(self):
        """Удаление группы обычным пользователем - отказ."""
        from catalog.models import CharacteristicGroup
        group = CharacteristicGroup.objects.create(name='To Delete', category=self.category)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/catalog/characteristic-groups/{group.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_group_not_found(self):
        """Удаление несуществующей группы - 404."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/catalog/characteristic-groups/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)