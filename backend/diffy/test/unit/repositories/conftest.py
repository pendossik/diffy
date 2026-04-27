import pytest
from catalog.models import Category, Product, CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


@pytest.fixture
def category(db):
    return Category.objects.create(name='Test Category')


@pytest.fixture
def categories_batch(db):
    categories = ['Electronics', 'Phones', 'Laptops', 'Tablets', 'Accessories']
    return [Category.objects.create(name=name) for name in categories]


@pytest.fixture
def category_with_products(db):
    category = Category.objects.create(name='Electronics')
    Product.objects.create(name='Laptop', category=category)
    Product.objects.create(name='Phone', category=category)
    return category


@pytest.fixture
def product(db, category):
    return Product.objects.create(name='Test Product', category=category)


@pytest.fixture
def characteristic_group(db, category):
    return CharacteristicGroup.objects.create(name='Specs', category=category, order=1)


@pytest.fixture
def characteristic_template(db, characteristic_group):
    return CharacteristicTemplate.objects.create(name='CPU', group=characteristic_group, order=1)


@pytest.fixture
def characteristic_value(db, product, characteristic_template):
    return CharacteristicValue.objects.create(
        product=product,
        template=characteristic_template,
        value='Intel i7'
    )