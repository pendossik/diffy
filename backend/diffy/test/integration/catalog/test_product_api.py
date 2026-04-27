"""Интеграционные тесты для API товаров."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class ProductAPITestCase(TestCase):
    """Тесты API товаров."""

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

    def test_list_products_unauthenticated(self):
        """Получение списка товаров без авторизации - успех."""
        response = self.client.get('/api/catalog/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_products_with_data(self):
        """Получение списка товаров с данными."""
        from catalog.models import Product
        Product.objects.create(name='Product 1', category=self.category)
        Product.objects.create(name='Product 2', category=self.category)

        response = self.client.get('/api/catalog/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_products_with_search(self):
        """Поиск товаров."""
        from catalog.models import Product
        Product.objects.create(name='iPhone 15', category=self.category)
        Product.objects.create(name='iPhone 16', category=self.category)
        Product.objects.create(name='Samsung', category=self.category)

        response = self.client.get('/api/catalog/products/?search=iphone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_products_filter_by_category(self):
        """Фильтрация товаров по категории."""
        from catalog.models import Product
        Product.objects.create(name='Phone 1', category=self.category)
        other_category = self.category.__class__.objects.create(name='Other')
        Product.objects.create(name='Other Product', category=other_category)

        response = self.client.get(f'/api/catalog/products/?category_id={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Phone 1')

    def test_create_product_as_admin(self):
        """Создание товара администратором - успех."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Product',
            'category_id': self.category.id,
            'img_url': 'https://example.com/image.jpg'
        }
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')

    def test_create_product_as_regular_user(self):
        """Создание товара обычным пользователем - отказ."""
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Product', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_unauthenticated(self):
        """Создание товара без авторизации - отказ."""
        data = {'name': 'New Product', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_empty_name(self):
        """Создание товара с пустым названием - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': '', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_invalid_category(self):
        """Создание товара с несуществующей категорией - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Product', 'category_id': 999}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_name_too_long(self):
        """Создание товара с названием более 200 символов - ошибка."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'a' * 201, 'category_id': self.category.id}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_duplicate_name(self):
        """Создание товара с дублирующим названием - ошибка."""
        from catalog.models import Product
        Product.objects.create(name='Existing', category=self.category)
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Existing', 'category_id': self.category.id}
        response = self.client.post('/api/catalog/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_product(self):
        """Получение товара по ID - успех."""
        from catalog.models import Product
        product = Product.objects.create(name='Test Product', category=self.category)
        response = self.client.get(f'/api/catalog/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_retrieve_product_not_found(self):
        """Получение несуществующего товара - 404."""
        response = self.client.get('/api/catalog/products/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_as_admin(self):
        """Обновление товара администратором - успех."""
        from catalog.models import Product
        product = Product.objects.create(name='Old Name', category=self.category)
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/products/{product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_update_product_as_regular_user(self):
        """Обновление товара обычным пользователем - отказ."""
        from catalog.models import Product
        product = Product.objects.create(name='Test', category=self.category)
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Name'}
        response = self.client.put(f'/api/catalog/products/{product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_not_found(self):
        """Обновление несуществующего товара - 404."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Name'}
        response = self.client.put('/api/catalog/products/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_as_admin(self):
        """Удаление товара администратором - успех."""
        from catalog.models import Product
        product = Product.objects.create(name='To Delete', category=self.category)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/catalog/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_product_as_regular_user(self):
        """Удаление товара обычным пользователем - отказ."""
        from catalog.models import Product
        product = Product.objects.create(name='To Delete', category=self.category)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f'/api/catalog/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_not_found(self):
        """Удаление несуществующего товара - 404."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete('/api/catalog/products/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)