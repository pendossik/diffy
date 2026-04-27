import pytest
from catalog.models import Category, Product, CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


@pytest.fixture
def cleanup_categories():
    yield
    CharacteristicValue.objects.all().delete()
    CharacteristicTemplate.objects.all().delete()
    CharacteristicGroup.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()


@pytest.fixture
def cleanup_products():
    yield
    CharacteristicValue.objects.all().delete()
    Product.objects.all().delete()


@pytest.fixture
def char_category(db):
    return Category.objects.create(name='Electronics')


@pytest.fixture
def group(db, char_category):
    return CharacteristicGroup.objects.create(category=char_category, name='Basic specs', order=1)


@pytest.fixture
def template(db, group):
    return CharacteristicTemplate.objects.create(group=group, name='Weight', order=1)


@pytest.fixture
def char_product(db, char_category):
    return Product.objects.create(name='Smartphone', category=char_category)


@pytest.fixture
def char_value(db, char_product, template):
    return CharacteristicValue.objects.create(product=char_product, template=template, value='200g')


@pytest.fixture
def group(db, char_category):
    return CharacteristicGroup.objects.create(category=char_category, name='Basic specs', order=1)


@pytest.fixture
def template(db, group):
    return CharacteristicTemplate.objects.create(group=group, name='Weight', order=1)


@pytest.fixture
def char_product(db, char_category):
    return Product.objects.create(name='Smartphone', category=char_category)


@pytest.fixture
def char_value(db, char_product, template):
    return CharacteristicValue.objects.create(product=char_product, template=template, value='200g')