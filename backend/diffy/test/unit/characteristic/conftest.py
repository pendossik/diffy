"""Локальные фикстуры для unit-тестов characteristic."""
import pytest
from categories.models import Category
from products.models import Product
from characteristic.models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


@pytest.fixture
def char_category(db):
    """Тестовая категория для characteristic."""
    return Category.objects.create(
        name='Электроника',
        name_ru='Электроника',
        name_en='Electronics'
    )


@pytest.fixture
def group(db, char_category):
    """Тестовая группа характеристик."""
    return CharacteristicGroup.objects.create(
        category=char_category,
        name='Основные параметры',
        name_ru='Основные параметры',
        name_en='Basic specs',
        order=1
    )


@pytest.fixture
def template(db, group):
    """Тестовый шаблон характеристики."""
    return CharacteristicTemplate.objects.create(
        group=group,
        name='Вес',
        name_ru='Вес',
        name_en='Weight',
        order=1
    )


@pytest.fixture
def char_product(db, char_category):
    """Тестовый товар для characteristic."""
    return Product.objects.create(
        name='Смартфон',
        name_ru='Смартфон',
        name_en='Smartphone',
        category=char_category
    )


@pytest.fixture
def char_value(db, char_product, template):
    """Тестовое значение характеристики."""
    return CharacteristicValue.objects.create(
        product=char_product,
        template=template,
        value='200г',
        value_ru='200г',
        value_en='200g'
    )
