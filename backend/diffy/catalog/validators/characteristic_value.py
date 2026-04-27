from catalog.validators.exceptions import (
    FieldRequiredError,
    FieldMaxLengthError,
    FieldEmptyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)


class CharacteristicValueValidator:
    MAX_VALUE_LENGTH = 200

    @staticmethod
    def validate_value(value: str, field_name: str = "value") -> None:
        if value is None:
            raise FieldRequiredError(field_name)

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        if not value:
            raise FieldEmptyError(field_name)

        if len(value) > CharacteristicValueValidator.MAX_VALUE_LENGTH:
            raise FieldMaxLengthError(field_name, CharacteristicValueValidator.MAX_VALUE_LENGTH)

    @staticmethod
    def validate_product_id(product_id: int) -> None:
        if product_id is None:
            raise FieldRequiredError("product_id")

        from catalog.models import Product
        if not Product.objects.filter(pk=product_id).exists():
            raise ObjectNotFoundError("Product", product_id)

    @staticmethod
    def validate_template_id(template_id: int) -> None:
        if template_id is None:
            raise FieldRequiredError("template_id")

        from catalog.models import CharacteristicTemplate
        if not CharacteristicTemplate.objects.filter(pk=template_id).exists():
            raise ObjectNotFoundError("CharacteristicTemplate", template_id)

    @staticmethod
    def validate_unique_product_template(product_id: int, template_id: int, value_id: int = None) -> None:
        from catalog.models import CharacteristicValue

        query = CharacteristicValue.objects.filter(
            product_id=product_id,
            template_id=template_id
        )
        if value_id:
            query = query.exclude(pk=value_id)

        if query.exists():
            raise ObjectAlreadyExistsError("CharacteristicValue", "product+template", f"{product_id}+{template_id}")