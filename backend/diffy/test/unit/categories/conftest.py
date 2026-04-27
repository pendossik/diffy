import pytest


@pytest.fixture
def cleanup_categories():
    yield
    from catalog.models import Category, Product
    Product.objects.all().delete()
    Category.objects.all().delete()


@pytest.fixture
def many_categories(cleanup_categories):
    categories = [Category.objects.create(name=f'Category {i:02d}') for i in range(1, 26)]
    return categories


@pytest.fixture
def searchable_categories(cleanup_categories):
    return {
        'electronics': Category.objects.create(name='Electronics'),
        'phones': Category.objects.create(name='Phones'),
        'laptops': Category.objects.create(name='Laptops'),
    }