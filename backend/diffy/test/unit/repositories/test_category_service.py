import pytest
from unittest.mock import MagicMock, patch
from catalog.services import CategoryService
from catalog.services.exceptions import PermissionDeniedError, ObjectNotFoundError
from catalog.repositories import CategoryRepository
from catalog.validators.exceptions import ValidationError


class TestCategoryService:
    def test_get_list_returns_data(self):
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [{'id': 1, 'name': 'Test'}]
        service = CategoryService(mock_repo)
        
        result = service.get_list(search='test')
        
        assert result == [{'id': 1, 'name': 'Test'}]
        mock_repo.get_all.assert_called_once_with(search='test', page=1, page_size=20)

    def test_get_by_id_returns_data(self):
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = {'id': 1, 'name': 'Test'}
        service = CategoryService(mock_repo)
        
        result = service.get_by_id(1)
        
        assert result == {'id': 1, 'name': 'Test'}

    def test_create_raises_permission_denied_for_non_admin(self, user):
        mock_repo = MagicMock()
        service = CategoryService(mock_repo)
        
        with pytest.raises(PermissionDeniedError):
            service.create(None, 'Test')

    def test_create_validates_name(self):
        mock_repo = MagicMock()
        service = CategoryService(mock_repo)
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        
        with pytest.raises(ValidationError):
            service.create(mock_user, '')
        
        with pytest.raises(ValidationError):
            service.create(mock_user, 'a' * 201)

    def test_create_success(self):
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = []
        service = CategoryService(mock_repo)
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.role = 'admin'
        mock_repo.create.return_value = {'id': 1, 'name': 'Test'}
        
        result = service.create(mock_user, 'Test')
        
        assert result == {'id': 1, 'name': 'Test'}
        mock_repo.create.assert_called_once_with(name='Test')

    def test_update_raises_permission_denied_for_non_admin(self):
        mock_repo = MagicMock()
        service = CategoryService(mock_repo)
        
        with pytest.raises(PermissionDeniedError):
            service.update(None, 1, 'Test')

    def test_delete_raises_permission_denied_for_non_admin(self):
        mock_repo = MagicMock()
        service = CategoryService(mock_repo)
        
        with pytest.raises(PermissionDeniedError):
            service.delete(None, 1)