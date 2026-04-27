import pytest
from catalog.repositories import CategoryRepository
from catalog.models import Category
from infrastructure.exceptions import ObjectNotFoundError


class TestCategoryRepository:
    @pytest.mark.django_db
    def test_get_all_returns_categories(self, category):
        result = CategoryRepository().get_all()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'Test Category'

    @pytest.mark.django_db
    def test_get_all_with_pagination(self, categories_batch):
        result = CategoryRepository().get_all(page=1, page_size=2)
        assert len(result) == 2

    @pytest.mark.django_db
    def test_get_all_with_search(self, categories_batch):
        result = CategoryRepository().get_all(search='Phone')
        assert len(result) == 1
        assert result[0]['name'] == 'Phones'

    @pytest.mark.django_db
    def test_get_all_paginated(self, categories_batch):
        result = CategoryRepository().get_all_paginated(page=1, page_size=3)
        assert result.total == 5
        assert result.page == 1
        assert result.total_pages == 2

    @pytest.mark.django_db
    def test_get_by_id(self, category):
        result = CategoryRepository().get_by_id(category.id)
        assert result['name'] == 'Test Category'

    @pytest.mark.django_db
    def test_get_by_id_not_found(self):
        with pytest.raises(ObjectNotFoundError):
            CategoryRepository().get_by_id(99999)

    @pytest.mark.django_db
    def test_create(self):
        result = CategoryRepository().create(name='New Category')
        assert result['name'] == 'New Category'

    @pytest.mark.django_db
    def test_update(self, category):
        result = CategoryRepository().update(category.id, name='Updated')
        assert result['name'] == 'Updated'

    @pytest.mark.django_db
    def test_delete(self, category):
        result = CategoryRepository().delete(category.id)
        assert result is True