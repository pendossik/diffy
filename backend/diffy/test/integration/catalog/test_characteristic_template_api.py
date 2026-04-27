"""Интеграционные тесты для API шаблонов характеристик."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CharacteristicTemplateAPITestCase(TestCase):
    """Тесты API шаблонов характеристик."""

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
        from catalog.models import Category, CharacteristicGroup
        self.category = Category.objects.create(name='Test Category')
        self.group = CharacteristicGroup.objects.create(name='Specs', category=self.category)

    def test_list_templates_unauthenticated(self):
        """Получение списка шаблонов без авторизации - успех."""
        response = self.client.get('/api/catalog/characteristic-templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_templates_with_data(self):
        """Получение списка шаблонов с данными."""
        from catalog.models import CharacteristicTemplate
        CharacteristicTemplate.objects.create(name='CPU', group=self.group)
        CharacteristicTemplate.objects.create(name='RAM', group=self.group)

        response = self.client.get('/api/catalog/characteristic-templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_templates_filter_by_group(self):
        """Фильтрация шаблонов по группе."""
        from catalog.models import CharacteristicTemplate
        CharacteristicTemplate.objects.create(name='CPU', group=self.group)
        other_group = self.group.__class__.objects.create(name='Other', category=self.category)
        CharacteristicTemplate.objects.create(name='Other', group=other_group)

        response = self.client.get(f'/api/catalog/characteristic-templates/?group_id={self.group.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_template_as_admin(self):
        """Создание шаблона администратором - успех."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Template', 'group_id': self.group.id}
        response = self.client.post('/api/catalog/characteristic-templates/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Template')

    def test_create_template_as_regular_user(self):
        """Создание шаблона обычным пользователем - отказ."""
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Template', 'group_id': self.group.id}
        response = self.client.post('/api/catalog/characteristic-templates/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_template_invalid_group(self):
        """Создание шаблона с несуществующей группой - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Template', 'group_id': 999}
        response = self.client.post('/api/catalog/characteristic-templates/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_template_empty_name(self):
        """Создание шаблона с пустым названием - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': '', 'group_id': self.group.id}
        response = self.client.post('/api/catalog/characteristic-templates/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_template_name_too_long(self):
        """Создание шаблона с названием более 100 символов - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'a' * 101, 'group_id': self.group.id}
        response = self.client.post('/api/catalog/characteristic-templates/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_template(self):
        """Получение шаблона по ID - успех."""
        from catalog.models import CharacteristicTemplate
        template = CharacteristicTemplate.objects.create(name='Test Template', group=self.group)
        response = self.client.get(f'/api/catalog/characteristic-templates/{template.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Template')

    def test_retrieve_template_not_found(self):
        """Получение несуществующего шаблона - 404."""
        response = self.client.get('/api/catalog/characteristic-templates/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_template_as_admin(self):
        """Обновление шаблона администратором - успех."""
        from catalog.models import CharacteristicTemplate
        template = CharacteristicTemplate.objects.create(name='Old Name', group=self.group)
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/characteristic-templates/{template.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_update_template_as_regular_user(self):
        """Обновление шаблона обычным пользователем - отказ."""
        from catalog.models import CharacteristicTemplate
        template = CharacteristicTemplate.objects.create(name='Test', group=self.group)
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/characteristic-templates/{template.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_template_not_found(self):
        """Обновление несуществующего шаблона - 404."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put('/api/catalog/characteristic-templates/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_template_as_admin(self):
        """Удаление шаблона администратором - успех."""
        from catalog.models import CharacteristicTemplate
        template = CharacteristicTemplate.objects.create(name='To Delete', group=self.group)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/catalog/characteristic-templates/{template.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CharacteristicTemplate.objects.filter(id=template.id).exists())

    def test_delete_template_as_regular_user(self):
        """Удаление шаблона обычным пользователем - отказ."""
        from catalog.models import CharacteristicTemplate
        template = CharacteristicTemplate.objects.create(name='To Delete', group=self.group)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/catalog/characteristic-templates/{template.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_template_not_found(self):
        """Удаление несуществующего шаблона - 404."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/catalog/characteristic-templates/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)