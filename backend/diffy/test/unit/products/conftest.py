import pytest
from catalog.models import Category, Product


@pytest.fixture
def cleanup_products():
    yield
    Product.objects.all().delete()


@pytest.fixture
def cleanup_categories():
    yield
    Product.objects.all().delete()
    Category.objects.all().delete()


@pytest.fixture
def test_category(cleanup_categories):
    return Category.objects.create(name='Test Category')


@pytest.fixture
def test_category2(cleanup_categories):
    return Category.objects.create(name='Second Category')


@pytest.fixture
def test_product(cleanup_products, test_category):
    return Product.objects.create(name='Test Product', category=test_category)


@pytest.fixture
def many_products(cleanup_products, test_category):
    return [
        Product.objects.create(name=f'Product {i:02d}', category=test_category)
        for i in range(1, 26)
    ]