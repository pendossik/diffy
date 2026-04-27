import pytest
from catalog.repositories import ProductRepository
from catalog.models import Product
from infrastructure.exceptions import ObjectNotFoundError


@pytest.fixture
def product(db, category):
    return Product.objects.create(name='Test Product', category=category)


class TestProductRepository:
    @pytest.mark.django_db
    def test_get_all_returns_products(self, product):
        result = ProductRepository().get_all()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'Test Product'

    @pytest.mark.django_db
    def test_get_all_with_category_filter(self, category_with_products):
        result = ProductRepository().get_all(category_id=category_with_products.id)
        assert len(result) == 2

    @pytest.mark.django_db
    def test_get_all_with_search(self, product):
        result = ProductRepository().get_all(search='Test')
        assert len(result) == 1

    @pytest.mark.django_db
    def test_get_all_paginated(self, category_with_products):
        result = ProductRepository().get_all_paginated(page=1, page_size=1)
        assert result.total == 2
        assert len(result.items) == 1

    @pytest.mark.django_db
    def test_get_by_id(self, product):
        result = ProductRepository().get_by_id(product.id)
        assert result['name'] == 'Test Product'

    @pytest.mark.django_db
    def test_get_by_id_not_found(self):
        with pytest.raises(ObjectNotFoundError):
            ProductRepository().get_by_id(99999)

    @pytest.mark.django_db
    def test_create(self, category):
        result = ProductRepository().create(name='New Product', category_id=category.id)
        assert result['name'] == 'New Product'

    @pytest.mark.django_db
    def test_update(self, product):
        result = ProductRepository().update(product.id, name='Updated Product')
        assert result['name'] == 'Updated Product'

    @pytest.mark.django_db
    def test_delete(self, product):
        result = ProductRepository().delete(product.id)
        assert result is True