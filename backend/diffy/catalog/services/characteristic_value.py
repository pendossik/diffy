from catalog.services.base import BaseService
from catalog.services.exceptions import PermissionDeniedError
from catalog.repositories.characteristic_value import CharacteristicValueRepository
from catalog.validators.characteristic_value import CharacteristicValueValidator
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


class CharacteristicValueService(BaseService):
    _repository_class = CharacteristicValueRepository
    
    def __init__(self, repository=None):
        super().__init__(repository)

    def get_list(self, search: str = None, product_id: int = None, page: int = 1, page_size: int = 20):
        try:
            return self.repository.get_all(
                search=search,
                product_id=product_id,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            raise ValidationError("search", str(e))

    def get_by_id(self, value_id: int):
        try:
            return self.repository.get_by_id(value_id)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ValidationError("id", str(e))

    def create(self, user, product_id: int, template_id: int, value: str):
        self._check_admin(user, "create characteristic values")

        try:
            CharacteristicValueValidator.validate_product_id(product_id)
            CharacteristicValueValidator.validate_template_id(template_id)
            CharacteristicValueValidator.validate_value(value)
            CharacteristicValueValidator.validate_unique_product_template(product_id, template_id)
        except ValidationError:
            raise

        return self.repository.create(
            product_id=product_id,
            template_id=template_id,
            value=value
        )

    def update(self, user, value_id: int, value: str = None):
        self._check_admin(user, "update characteristic values")

        try:
            char_value = self.repository.get_by_id(value_id)
        except ObjectNotFoundError:
            raise

        try:
            if value:
                CharacteristicValueValidator.validate_value(value)
                if hasattr(char_value, 'product_id') and hasattr(char_value, 'template_id'):
                    CharacteristicValueValidator.validate_unique_product_template(
                        char_value.product_id,
                        char_value.template_id,
                        value_id
                    )
        except ValidationError:
            raise

        update_data = {}
        if value:
            update_data['value'] = value

        return self.repository.update(value_id, **update_data)

    def delete(self, user, value_id: int):
        self._check_admin(user, "delete characteristic values")

        try:
            self.repository.get_by_id(value_id)
        except ObjectNotFoundError:
            raise

        return self.repository.delete(value_id)