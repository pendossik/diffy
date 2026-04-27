from catalog.services.base import BaseService
from catalog.services.exceptions import PermissionDeniedError
from catalog.repositories.characteristic_template import CharacteristicTemplateRepository
from catalog.validators.characteristic_template import CharacteristicTemplateValidator
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


class CharacteristicTemplateService(BaseService):
    _repository_class = CharacteristicTemplateRepository
    
    def __init__(self, repository=None):
        super().__init__(repository)

    def get_list(self, search: str = None, group_id: int = None, page: int = 1, page_size: int = 20):
        try:
            return self.repository.get_all(
                search=search,
                group_id=group_id,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            raise ValidationError("search", str(e))

    def get_by_id(self, template_id: int):
        try:
            return self.repository.get_by_id(template_id)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ValidationError("id", str(e))

    def create(self, user, name: str, group_id: int, order: int = 0):
        self._check_admin(user, "create characteristic templates")

        try:
            CharacteristicTemplateValidator.validate_name(name)
            CharacteristicTemplateValidator.validate_group_id(group_id)
            CharacteristicTemplateValidator.validate_unique_name(name, group_id)
        except ValidationError:
            raise

        return self.repository.create(
            name=name,
            group_id=group_id,
            order=order
        )

    def update(self, user, template_id: int, name: str = None, order: int = None):
        self._check_admin(user, "update characteristic templates")

        try:
            template = self.repository.get_by_id(template_id)
        except ObjectNotFoundError:
            raise

        try:
            if name:
                CharacteristicTemplateValidator.validate_name(name)
                if hasattr(template, 'group_id'):
                    CharacteristicTemplateValidator.validate_unique_name(name, template.group_id, template_id)
        except ValidationError:
            raise

        update_data = {}
        if name:
            update_data['name'] = name
        if order is not None:
            update_data['order'] = order

        return self.repository.update(template_id, **update_data)

    def delete(self, user, template_id: int):
        self._check_admin(user, "delete characteristic templates")

        try:
            self.repository.get_by_id(template_id)
        except ObjectNotFoundError:
            raise

        return self.repository.delete(template_id)