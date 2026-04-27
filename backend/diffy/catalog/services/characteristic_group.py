from catalog.services.base import BaseService
from catalog.services.exceptions import PermissionDeniedError
from catalog.repositories.characteristic_group import CharacteristicGroupRepository
from catalog.validators.characteristic_group import CharacteristicGroupValidator
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


class CharacteristicGroupService(BaseService):
    _repository_class = CharacteristicGroupRepository
    
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

    def get_by_id(self, group_id: int):
        try:
            return self.repository.get_by_id(group_id)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ValidationError("id", str(e))

    def create(self, user, name: str, category_id: int, order: int = 0):
        self._check_admin(user, "create characteristic groups")

        try:
            CharacteristicGroupValidator.validate_name(name)
            CharacteristicGroupValidator.validate_category_id(category_id)
            CharacteristicGroupValidator.validate_unique_name(name, category_id)
        except ValidationError:
            raise

        return self.repository.create(
            name=name,
            category_id=category_id,
            order=order
        )

    def update(self, user, group_id: int, name: str = None, category_id: int = None, order: int = None):
        self._check_admin(user, "update characteristic groups")

        try:
            group = self.repository.get_by_id(group_id)
        except ObjectNotFoundError:
            raise

        try:
            if name:
                CharacteristicGroupValidator.validate_name(name)
                check_category_id = category_id or group.get('category_id')
                CharacteristicGroupValidator.validate_unique_name(name, check_category_id, group_id)
            if category_id:
                CharacteristicGroupValidator.validate_category_id(category_id)
        except ValidationError:
            raise

        update_data = {}
        if name:
            update_data['name'] = name
        if category_id:
            update_data['category_id'] = category_id
        if order is not None:
            update_data['order'] = order

        return self.repository.update(group_id, **update_data)

    def delete(self, user, group_id: int):
        self._check_admin(user, "delete characteristic groups")

        try:
            self.repository.get_by_id(group_id)
        except ObjectNotFoundError:
            raise

        return self.repository.delete(group_id)