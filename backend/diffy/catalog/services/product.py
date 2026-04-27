from catalog.services.base import BaseService
from catalog.services.exceptions import PermissionDeniedError
from catalog.repositories.product import ProductRepository
from catalog.validators.product import ProductValidator
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


class ProductService(BaseService):
    _repository_class = ProductRepository
    
    def __init__(self, repository=None):
        super().__init__(repository)

    def get_list(self, search: str = None, category_id: int = None, page: int = 1, page_size: int = 20):
        try:
            return self.repository.get_all(
                search=search,
                category_id=category_id,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            raise ValidationError("search", str(e))

    def get_by_id(self, product_id: int):
        try:
            return self.repository.get_by_id(product_id)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ValidationError("id", str(e))

    def create(self, user, name: str, category_id: int, img_url: str = None):
        self._check_admin(user, "create products")

        try:
            ProductValidator.validate_name(name)
            ProductValidator.validate_category_id(category_id)
            ProductValidator.validate_unique_name(name, category_id)
            ProductValidator.validate_img_url(img_url) if img_url else None
        except ValidationError:
            raise

        return self.repository.create(
            name=name,
            category_id=category_id,
            img_url=img_url
        )

    def update(self, user, product_id: int, name: str = None, category_id: int = None, img_url: str = None):
        self._check_admin(user, "update products")

        try:
            product = self.repository.get_by_id(product_id)
        except ObjectNotFoundError:
            raise

        try:
            if name:
                ProductValidator.validate_name(name)
                check_category_id = category_id or product.get('category_id') or product.get('category')
                if isinstance(product, dict):
                    check_category_id = check_category_id or product.get('category_id')
                else:
                    check_category_id = check_category_id or (hasattr(product, 'category_id') and product.category_id)
                ProductValidator.validate_unique_name(name, check_category_id, product_id)

            if category_id:
                ProductValidator.validate_category_id(category_id)

            if img_url is not None:
                ProductValidator.validate_img_url(img_url)
        except ValidationError:
            raise

        update_data = {}
        if name:
            update_data['name'] = name
        if category_id:
            update_data['category_id'] = category_id
        if img_url is not None:
            update_data['img_url'] = img_url

        return self.repository.update(product_id, **update_data)

    def delete(self, user, product_id: int):
        self._check_admin(user, "delete products")

        try:
            self.repository.get_by_id(product_id)
        except ObjectNotFoundError:
            raise

        return self.repository.delete(product_id)