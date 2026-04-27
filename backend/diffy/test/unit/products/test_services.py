import pytest
from unittest.mock import MagicMock
from catalog.services.product import ProductService
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError
from catalog.validators.exceptions import ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError


@pytest.mark.django_db
class TestProductServiceCreate:
    @pytest.fixture
    def category(self, cleanup_categories):
        from catalog.models import Category
        return Category.objects.create(name='Test Category')

    def test_create_raises_permission_denied_for_none_user(self):
        service = ProductService()
        
        with pytest.raises(PermissionDeniedError):
            service.create(None, 'Test', 1)

    def test_create_raises_permission_denied_for_anonymous(self, category):
        service = ProductService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Test', category.id)

    def test_create_raises_permission_denied_for_regular_user(self, category):
        service = ProductService()
        user = MagicMock()
        user.is_authenticated = True
        user.role = None
        user.is_staff = False
        user.is_superuser = False
        
        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Test', category.id)

    def test_create_success_for_admin(self, category):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.create(user, 'Test', category.id)
        
        assert result['name'] == 'Test'
        assert result['category_id'] == category.id

    def test_create_validates_empty_name(self, category):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, '', category.id)

    def test_create_validates_name_length(self, category):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, 'a' * 201, category.id)

    def test_create_validates_category(self, cleanup_categories):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.create(user, 'Test', 999)

    def test_create_validates_duplicate_name(self, category):
        from catalog.models import Product
        Product.objects.create(name='Existing', category=category)
        
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.create(user, 'Existing', category.id)


@pytest.mark.django_db
class TestProductServiceUpdate:
    @pytest.fixture
    def product(self, test_product):
        return test_product

    def test_update_raises_permission_denied_for_none_user(self):
        service = ProductService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(None, 1, 'New')

    def test_update_raises_permission_denied_for_anonymous(self, product):
        service = ProductService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.update(user, product.id, 'New')

    def test_update_raises_permission_denied_for_non_admin(self, product, regular_user):
        service = ProductService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(regular_user, product.id, 'New')

    def test_update_raises_not_found(self, cleanup_products):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.update(user, 999, 'New')

    def test_update_success_without_name(self, product):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.update(user, product.id, category_id=None)
        
        assert result['name'] == product.name
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises(ValidationError):
            service.update(user, product.id, 'a' * 201)

    def test_update_success_without_name(self, product):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.update(user, product.id, category_id=None)
        
        assert result['name'] == product.name

    def test_update_success(self, product):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.update(user, product.id, 'New')
        
        assert result['name'] == 'New'


@pytest.mark.django_db
class TestProductServiceDelete:
    @pytest.fixture
    def product(self, test_product):
        return test_product

    def test_delete_raises_permission_denied_for_none_user(self):
        service = ProductService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(None, 1)

    def test_delete_raises_permission_denied_for_anonymous(self, product):
        service = ProductService()
        user = MagicMock()
        user.is_authenticated = False
        
        with pytest.raises(PermissionDeniedError):
            service.delete(user, product.id)

    def test_delete_raises_permission_denied_for_non_admin(self, product, regular_user):
        service = ProductService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(regular_user, product.id)

    def test_delete_raises_not_found(self, cleanup_products):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.delete(user, 999)

    def test_delete_success(self, product):
        service = ProductService()
        
        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'
        
        result = service.delete(user, product.id)
        
        assert result is True