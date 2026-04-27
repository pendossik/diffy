import pytest
from unittest.mock import MagicMock
from catalog.services.characteristic_group import CharacteristicGroupService
from catalog.services.characteristic_template import CharacteristicTemplateService
from catalog.services.characteristic_value import CharacteristicValueService
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError
from catalog.validators.exceptions import ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError


@pytest.mark.django_db
class TestCharacteristicGroupServiceCreate:
    @pytest.fixture
    def category(self, cleanup_categories):
        from catalog.models import Category
        return Category.objects.create(name='Test Category')

    def test_create_raises_permission_denied_for_none_user(self, category):
        service = CharacteristicGroupService()

        with pytest.raises(PermissionDeniedError):
            service.create(None, 'Specs', category.id)

    def test_create_raises_permission_denied_for_anonymous(self, category):
        service = CharacteristicGroupService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Specs', category.id)

    def test_create_raises_permission_denied_for_regular_user(self, category):
        service = CharacteristicGroupService()
        user = MagicMock()
        user.is_authenticated = True
        user.role = None
        user.is_staff = False
        user.is_superuser = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, 'Specs', category.id)

    def test_create_validates_empty_name(self, category):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, '', category.id)

    def test_create_validates_name_length(self, category):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, 'a' * 101, category.id)

    def test_create_validates_category(self, cleanup_categories):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.create(user, 'Specs', 999)

    def test_create_success_for_admin(self, category):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.create(user, 'Specs', category.id)

        assert result['name'] == 'Specs'
        assert result['category_id'] == category.id


@pytest.mark.django_db
class TestCharacteristicGroupServiceUpdate:
    @pytest.fixture
    def group(self, cleanup_categories):
        from catalog.models import Category, CharacteristicGroup
        category = Category.objects.create(name='Test Category')
        return CharacteristicGroup.objects.create(name='Specs', category=category)

    def test_update_raises_permission_denied_for_none_user(self, group):
        service = CharacteristicGroupService()

        with pytest.raises(PermissionDeniedError):
            service.update(None, group.id, 'New Name')

    def test_update_raises_permission_denied_for_anonymous(self, group):
        service = CharacteristicGroupService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.update(user, group.id, 'New Name')

    def test_update_raises_permission_denied_for_non_admin(self, group, regular_user):
        service = CharacteristicGroupService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(regular_user, group.id, 'New Name')

    def test_update_raises_not_found(self, cleanup_categories):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.update(user, 999, 'New Name')

    def test_update_success(self, group):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.update(user, group.id, 'New Specs')

        assert result['name'] == 'New Specs'


@pytest.mark.django_db
class TestCharacteristicGroupServiceDelete:
    @pytest.fixture
    def group(self, cleanup_categories):
        from catalog.models import Category, CharacteristicGroup
        category = Category.objects.create(name='Test Category')
        return CharacteristicGroup.objects.create(name='Specs', category=category)

    def test_delete_raises_permission_denied_for_none_user(self, group):
        service = CharacteristicGroupService()

        with pytest.raises(PermissionDeniedError):
            service.delete(None, group.id)

    def test_delete_raises_permission_denied_for_anonymous(self, group):
        service = CharacteristicGroupService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.delete(user, group.id)

    def test_delete_raises_permission_denied_for_non_admin(self, group, regular_user):
        service = CharacteristicGroupService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(regular_user, group.id)

    def test_delete_raises_not_found(self, cleanup_categories):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.delete(user, 999)

    def test_delete_success_for_admin(self, group):
        service = CharacteristicGroupService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.delete(user, group.id)

        assert result is True


@pytest.mark.django_db
class TestCharacteristicTemplateServiceCreate:
    @pytest.fixture
    def group(self, cleanup_categories):
        from catalog.models import Category, CharacteristicGroup
        category = Category.objects.create(name='Test Category')
        return CharacteristicGroup.objects.create(name='Specs', category=category)

    def test_create_raises_permission_denied_for_none_user(self, group):
        service = CharacteristicTemplateService()

        with pytest.raises(PermissionDeniedError):
            service.create(None, 'CPU', group.id)

    def test_create_raises_permission_denied_for_anonymous(self, group):
        service = CharacteristicTemplateService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, 'CPU', group.id)

    def test_create_raises_permission_denied_for_regular_user(self, group):
        service = CharacteristicTemplateService()
        user = MagicMock()
        user.is_authenticated = True
        user.role = None
        user.is_staff = False
        user.is_superuser = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, 'CPU', group.id)

    def test_create_validates_empty_name(self, group):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, '', group.id)

    def test_create_validates_name_length(self, group):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, 'a' * 101, group.id)

    def test_create_validates_group(self, cleanup_categories):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.create(user, 'CPU', 999)

    def test_create_success_for_admin(self, group):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.create(user, 'CPU', group.id)

        assert result['name'] == 'CPU'
        assert result['group_id'] == group.id


@pytest.mark.django_db
class TestCharacteristicTemplateServiceUpdate:
    @pytest.fixture
    def template(self, cleanup_categories):
        from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate
        category = Category.objects.create(name='Test Category')
        group = CharacteristicGroup.objects.create(name='Specs', category=category)
        return CharacteristicTemplate.objects.create(name='CPU', group=group)

    def test_update_raises_permission_denied_for_none_user(self, template):
        service = CharacteristicTemplateService()

        with pytest.raises(PermissionDeniedError):
            service.update(None, template.id, 'New CPU')

    def test_update_raises_permission_denied_for_non_admin(self, template, regular_user):
        service = CharacteristicTemplateService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(regular_user, template.id, 'New CPU')

    def test_update_raises_not_found(self, cleanup_categories):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.update(user, 999, 'New CPU')

    def test_update_success(self, template):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.update(user, template.id, 'New CPU')

        assert result['name'] == 'New CPU'


@pytest.mark.django_db
class TestCharacteristicTemplateServiceDelete:
    @pytest.fixture
    def template(self, cleanup_categories):
        from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate
        category = Category.objects.create(name='Test Category')
        group = CharacteristicGroup.objects.create(name='Specs', category=category)
        return CharacteristicTemplate.objects.create(name='CPU', group=group)

    def test_delete_raises_permission_denied_for_none_user(self, template):
        service = CharacteristicTemplateService()

        with pytest.raises(PermissionDeniedError):
            service.delete(None, template.id)

    def test_delete_raises_permission_denied_for_non_admin(self, template, regular_user):
        service = CharacteristicTemplateService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(regular_user, template.id)

    def test_delete_raises_not_found(self, cleanup_categories):
        service = CharacteristicTemplateService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.delete(user, 999)


@pytest.mark.django_db
class TestCharacteristicValueServiceCreate:
    @pytest.fixture
    def category(self, cleanup_categories):
        from catalog.models import Category
        return Category.objects.create(name='Test Category')

    @pytest.fixture
    def product(self, cleanup_products, category):
        from catalog.models import Product
        return Product.objects.create(name='Test Product', category=category)

    @pytest.fixture
    def template(self, cleanup_categories, category):
        from catalog.models import CharacteristicGroup, CharacteristicTemplate
        group = CharacteristicGroup.objects.create(name='Specs', category=category)
        return CharacteristicTemplate.objects.create(name='CPU', group=group)

    def test_create_raises_permission_denied_for_none_user(self, product, template):
        service = CharacteristicValueService()

        with pytest.raises(PermissionDeniedError):
            service.create(None, product.id, template.id, 'Intel i7')

    def test_create_raises_permission_denied_for_anonymous(self, product, template):
        service = CharacteristicValueService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, product.id, template.id, 'Intel i7')

    def test_create_raises_permission_denied_for_regular_user(self, product, template):
        service = CharacteristicValueService()
        user = MagicMock()
        user.is_authenticated = True
        user.role = None
        user.is_staff = False
        user.is_superuser = False

        with pytest.raises(PermissionDeniedError):
            service.create(user, product.id, template.id, 'Intel i7')

    def test_create_validates_empty_value(self, product, template):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, product.id, template.id, '')

    def test_create_validates_value_length(self, product, template):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises(ValidationError):
            service.create(user, product.id, template.id, 'a' * 501)

    def test_create_validates_product(self, cleanup_categories, template):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.create(user, 999, template.id, 'Intel i7')

    def test_create_validates_template(self, cleanup_products, category):
        from catalog.models import Product
        product = Product.objects.create(name='Test Product', category=category)

        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.create(user, product.id, 999, 'Intel i7')

    def test_create_success_for_admin(self, product, template):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.create(user, product.id, template.id, 'Intel i7')

        assert result['value'] == 'Intel i7'


@pytest.mark.django_db
class TestCharacteristicValueServiceUpdate:
    @pytest.fixture
    def value(self, cleanup_categories, cleanup_products):
        from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate, Product
        category = Category.objects.create(name='Test Category')
        group = CharacteristicGroup.objects.create(name='Specs', category=category)
        template = CharacteristicTemplate.objects.create(name='CPU', group=group)
        product = Product.objects.create(name='Test Product', category=category)
        from catalog.models import CharacteristicValue
        return CharacteristicValue.objects.create(product=product, template=template, value='Intel i7')

    def test_update_raises_permission_denied_for_none_user(self, value):
        service = CharacteristicValueService()

        with pytest.raises(PermissionDeniedError):
            service.update(None, value.id, 'AMD Ryzen')

    def test_update_raises_permission_denied_for_anonymous(self, value):
        service = CharacteristicValueService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.update(user, value.id, 'AMD Ryzen')

    def test_update_raises_permission_denied_for_non_admin(self, value, regular_user):
        service = CharacteristicValueService()
        
        with pytest.raises(PermissionDeniedError):
            service.update(regular_user, value.id, 'AMD Ryzen')

    def test_update_raises_not_found(self, cleanup_categories, cleanup_products):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.update(user, 999, 'AMD Ryzen')

    def test_update_success(self, value):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.update(user, value.id, 'AMD Ryzen')

        assert result['value'] == 'AMD Ryzen'


@pytest.mark.django_db
class TestCharacteristicValueServiceDelete:
    @pytest.fixture
    def value(self, cleanup_categories, cleanup_products):
        from catalog.models import Category, CharacteristicGroup, CharacteristicTemplate, Product
        category = Category.objects.create(name='Test Category')
        group = CharacteristicGroup.objects.create(name='Specs', category=category)
        template = CharacteristicTemplate.objects.create(name='CPU', group=group)
        product = Product.objects.create(name='Test Product', category=category)
        from catalog.models import CharacteristicValue
        return CharacteristicValue.objects.create(product=product, template=template, value='Intel i7')

    def test_delete_raises_permission_denied_for_none_user(self, value):
        service = CharacteristicValueService()

        with pytest.raises(PermissionDeniedError):
            service.delete(None, value.id)

    def test_delete_raises_permission_denied_for_anonymous(self, value):
        service = CharacteristicValueService()
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(PermissionDeniedError):
            service.delete(user, value.id)

    def test_delete_raises_permission_denied_for_non_admin(self, value, regular_user):
        service = CharacteristicValueService()
        
        with pytest.raises(PermissionDeniedError):
            service.delete(regular_user, value.id)

    def test_delete_raises_not_found(self, cleanup_categories, cleanup_products):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        with pytest.raises((CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)):
            service.delete(user, 999)

    def test_delete_success(self, value):
        service = CharacteristicValueService()

        user = MagicMock()
        user.is_authenticated = True
        user.role = 'admin'

        result = service.delete(user, value.id)

        assert result is True