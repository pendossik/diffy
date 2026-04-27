from catalog.services.base import BaseService
from catalog.services.exceptions import PermissionDeniedError
from catalog.repositories.category import CategoryRepository
from catalog.validators.category import CategoryValidator
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


class CategoryService(BaseService):
    _repository_class = CategoryRepository
    
    def __init__(self, repository=None):
        super().__init__(repository)

    def get_list(self, search: str = None, page: int = 1, page_size: int = 20):
        try:
            return self.repository.get_all(search=search, page=page, page_size=page_size)
        except Exception as e:
            raise ValidationError("search", str(e))

    def get_by_id(self, category_id: int):
        try:
            return self.repository.get_by_id(category_id)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ValidationError("id", str(e))

    def create(self, user, name: str):
        self._check_admin(user, "create categories")

        try:
            CategoryValidator.validate_name(name)
            CategoryValidator.validate_unique_name(name)
        except ValidationError:
            raise

        return self.repository.create(name=name)

    def update(self, user, category_id: int, name: str):
        self._check_admin(user, "update categories")

        try:
            self.repository.get_by_id(category_id)
        except ObjectNotFoundError:
            raise

        try:
            CategoryValidator.validate_name(name)
            CategoryValidator.validate_unique_name(name, category_id)
        except ValidationError:
            raise

        return self.repository.update(category_id, name=name)

    def delete(self, user, category_id: int):
        self._check_admin(user, "delete categories")

        try:
            category = self.repository.get_by_id(category_id)
        except ObjectNotFoundError:
            raise

        return self.repository.delete(category_id)