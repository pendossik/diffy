"""Интеграционные тесты для API значений характеристик."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class CharacteristicValueAPITestCase(TestCase):
    """Тесты API значений характеристик."""

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
        from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate, Product
        self.category = Category.objects.create(name='Test Category')
        self.group = CharacteristicGroup.objects.create(name='Specs', category=self.category)
        self.template = CharacteristicTemplate.objects.create(name='CPU', group=self.group)
        self.product = Product.objects.create(name='Test Product', category=self.category)

    def test_list_values_unauthenticated(self):
        """Получение списка значений без авторизации - успех."""
        response = self.client.get('/api/catalog/characteristic-values/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_values_with_data(self):
        """Получение списка значений с данными."""
        from catalog.models import CharacteristicValue
        CharacteristicValue.objects.create(product=self.product, template=self.template, value='Intel i7')
        CharacteristicValue.objects.create(product=self.product, template=self.template, value='AMD Ryzen')

        response = self.client.get('/api/catalog/characteristic-values/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_values_filter_by_product(self):
        """Фильтрация значений по товару."""
        from catalog.models import CharacteristicValue, CharacteristicTemplate
        other_template = CharacteristicTemplate.objects.create(name='RAM', group=self.group)
        CharacteristicValue.objects.create(product=self.product, template=self.template, value='Intel i7')
        other_product = self.product.__class__.objects.create(name='Other Product', category=self.category)
        CharacteristicValue.objects.create(product=other_product, template=self.template, value='AMD')

        response = self.client.get(f'/api/catalog/characteristic-values/?product_id={self.product.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_value_as_admin(self):
        """Создание значения администратором - успех."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_id': self.product.id,
            'template_id': self.template.id,
            'value': 'Intel i7'
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['value'], 'Intel i7')

    def test_create_value_as_regular_user(self):
        """Создание значения обычным пользователем - отказ."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'product_id': self.product.id,
            'template_id': self.template.id,
            'value': 'Intel i7'
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_value_invalid_product(self):
        """Создание значения с несуществующим товаром - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_id': 999,
            'template_id': self.template.id,
            'value': 'Intel i7'
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_value_invalid_template(self):
        """Создание значения с несуществующим шаблоном - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_id': self.product.id,
            'template_id': 999,
            'value': 'Intel i7'
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_value_empty_value(self):
        """Создание значения с пустым значением - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_id': self.product.id,
            'template_id': self.template.id,
            'value': ''
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_value_too_long(self):
        """Создание значения более 500 символов - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_id': self.product.id,
            'template_id': self.template.id,
            'value': 'a' * 501
        }
        response = self.client.post('/api/catalog/characteristic-values/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_value(self):
        """Получение значения по ID - успех."""
        from catalog.models import CharacteristicValue
        value = CharacteristicValue.objects.create(
            product=self.product, template=self.template, value='Intel i7'
        )
        response = self.client.get(f'/api/catalog/characteristic-values/{value.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Intel i7')

    def test_retrieve_value_not_found(self):
        """Получение несуществующего значения - 404."""
        response = self.client.get('/api/catalog/characteristic-values/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_value_as_admin(self):
        """Обновление значения администратором - успех."""
        from catalog.models import CharacteristicValue
        value = CharacteristicValue.objects.create(
            product=self.product, template=self.template, value='Old Value'
        )
        self.client.force_authenticate(user=self.admin_user)
        data = {'value': 'New Value'}
        response = self.client.put(f'/api/catalog/characteristic-values/{value.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'New Value')

    def test_update_value_as_regular_user(self):
        """Обновление значения обычным пользователем - отказ."""
        from catalog.models import CharacteristicValue
        value = CharacteristicValue.objects.create(
            product=self.product, template=self.template, value='Old Value'
        )
        self.client.force_authenticate(user=self.regular_user)
        data = {'value': 'New Value'}
        response = self.client.put(f'/api/catalog/characteristic-values/{value.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_value_not_found(self):
        """Обновление несуществующего значения - 404."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'value': 'New Value'}
        response = self.client.put('/api/catalog/characteristic-values/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_value_as_admin(self):
        """Удаление значения администратором - успех."""
        from catalog.models import CharacteristicValue
        value = CharacteristicValue.objects.create(
            product=self.product, template=self.template, value='To Delete'
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/catalog/characteristic-values/{value.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CharacteristicValue.objects.filter(id=value.id).exists())

    def test_delete_value_as_regular_user(self):
        """Удаление значения обычным пользователем - отказ."""
        from catalog.models import CharacteristicValue
        value = CharacteristicValue.objects.create(
            product=self.product, template=self.template, value='To Delete'
        )
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/catalog/characteristic-values/{value.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_value_not_found(self):
        """Удаление несуществующего значения - 404."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/catalog/characteristic-values/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)