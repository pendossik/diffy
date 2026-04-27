import pytest
from infrastructure.repositories.django_repository import DjangoRepository, PaginatedResult
from infrastructure.exceptions import ObjectNotFoundError
from catalog.models import Category


class TestCategoryRepository(DjangoRepository):
    model = Category


class TestDjangoRepository:
    @pytest.mark.django_db
    def test_get_all_returns_list(self, category):
        repo = TestCategoryRepository()
        result = repo.get_all()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'Test Category'

    @pytest.mark.django_db
    def test_get_all_with_pagination(self, categories_batch):
        repo = TestCategoryRepository()
        result = repo.get_all(page=1, page_size=2)
        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.django_db
    def test_get_all_with_search(self, categories_batch):
        repo = TestCategoryRepository()
        result = repo.get_all(search='Phone')
        assert len(result) == 1
        assert result[0]['name'] == 'Phones'

    @pytest.mark.django_db
    def test_get_all_with_filters(self, category_with_products):
        from catalog.models import Product
        repo = TestCategoryRepository()
        result = repo.get_all(category_id=category_with_products.id)
        assert len(result) == 2

    @pytest.mark.django_db
    def test_get_all_paginated_returns_paginated_result(self, categories_batch):
        repo = TestCategoryRepository()
        result = repo.get_all_paginated(page=1, page_size=2)
        assert isinstance(result, PaginatedResult)
        assert result.total == 5
        assert result.page == 1
        assert result.page_size == 2
        assert result.total_pages == 3
        assert len(result.items) == 2

    @pytest.mark.django_db
    def test_get_by_id_returns_dict(self, category):
        repo = TestCategoryRepository()
        result = repo.get_by_id(category.id)
        assert isinstance(result, dict)
        assert result['name'] == 'Test Category'
        assert result['id'] == category.id

    @pytest.mark.django_db
    def test_get_by_id_raises_not_found(self):
        repo = TestCategoryRepository()
        with pytest.raises(ObjectNotFoundError):
            repo.get_by_id(99999)

    @pytest.mark.django_db
    def test_create_returns_dict(self):
        repo = TestCategoryRepository()
        result = repo.create(name='New Category')
        assert isinstance(result, dict)
        assert result['name'] == 'New Category'

    @pytest.mark.django_db
    def test_update_returns_dict(self, category):
        repo = TestCategoryRepository()
        result = repo.update(category.id, name='Updated Category')
        assert isinstance(result, dict)
        assert result['name'] == 'Updated Category'

    @pytest.mark.django_db
    def test_delete_returns_true(self, category):
        repo = TestCategoryRepository()
        result = repo.delete(category.id)
        assert result is True
        with pytest.raises(ObjectNotFoundError):
            repo.get_by_id(category.id)

    @pytest.mark.django_db
    def test_list_alias_works(self, categories_batch):
        repo = TestCategoryRepository()
        result = repo.list()
        assert isinstance(result, list)
        assert len(result) == 5