import pytest
from unittest.mock import MagicMock
from catalog.services.category import CategoryService
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError
from catalog.validators.exceptions import ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError


@pytest.mark.django_db
class TestCategoryServiceCreate:
    def test_create_raises_permission_denied_for_none_user(self):
        service = CategoryService()
        
        with pytest.raises(PermissionDeniedError):
            service.create(None, 'Test')

    def test_create_raises_permission_denied_for_anonymous(self):
        service = CategoryService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Test')

    def test_create_raises_permission_denied_for_regular_user(self):
        service = CategoryService()
        user = MagicMock()
        user.is_authenticated = True
        user.role = None
        user.is_staff = False
        user.is_superuser = False
        
        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Test')

    def test_create_success_for_admin_user(self):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.is_staff = True
        user.role = None
        
        result = service.create(user, 'Test Category')
        
        assert result['name'] == 'Test Category'

    def test_create_success_for_superuser(self):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = True
        user.role = None
        
        result = service.create(user, 'Test Category')
        
        assert result['name'] == 'Test Category'

    def test_create_validates_empty_name(self):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, '')

    def test_create_validates_name_length(self):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, 'a' * 101)

    def test_create_validates_duplicate_name(self, cleanup_categories):
        from catalog.models import Category
        Category.objects.create(name='Existing')
        
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, 'Existing')


@pytest.mark.django_db
class TestCategoryServiceUpdate:
    @pytest.fixture
    def category(self, cleanup_categories):
        from catalog.models import Category
        return Category.objects.create(name='Test Category')

    def test_update_raises_permission_denied_for_none_user(self):
        service = CategoryService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(None, 1, 'New Name')

    def test_update_raises_permission_denied_for_anonymous(self):
        service = CategoryService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.update(user, 1, 'New Name')

    def test_update_raises_permission_denied_for_non_admin(self, regular_user):
        service = CategoryService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(regular_user, 1, 'New Name')

    def test_update_raises_not_found_for_nonexistent(self, cleanup_categories):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.update(user, 999, 'New Name')

    def test_update_validates_empty_name(self, category):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.update(user, category.id, '')

    def test_update_validates_name_length(self, category):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.update(user, category.id, 'a' * 101)

    def test_update_validates_duplicate_name(self, cleanup_categories):
        from catalog.models import Category
        Category.objects.create(name='Existing')
        cat = Category.objects.create(name='ToUpdate')
        
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.update(user, cat.id, 'Existing')

    def test_update_success(self, category):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.update(user, category.id, 'New Name')
        
        assert result['name'] == 'New Name'


@pytest.mark.django_db
class TestCategoryServiceDelete:
    @pytest.fixture
    def category(self, cleanup_categories):
        from catalog.models import Category
        return Category.objects.create(name='Test Category')

    def test_delete_raises_permission_denied_for_none_user(self):
        service = CategoryService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(None, 1)

    def test_delete_raises_permission_denied_for_anonymous(self):
        service = CategoryService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.delete(user, 1)

    def test_delete_raises_permission_denied_for_non_admin(self, regular_user):
        service = CategoryService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(regular_user, 1)

    def test_delete_raises_not_found_for_nonexistent(self, cleanup_categories):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.delete(user, 999)

    def test_delete_success(self, category):
        service = CategoryService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.delete(user, category.id)
        
        assert result is True