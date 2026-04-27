from catalog.validators.exceptions import (
    FieldRequiredError,
    FieldMaxLengthError,
    FieldEmptyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)


class CharacteristicGroupValidator:
    MAX_NAME_LENGTH = 100

    @staticmethod
    def validate_name(name: str, field_name: str = "name") -> None:
        if name is None:
            raise FieldRequiredError(field_name)

        if not isinstance(name, str):
            name = str(name)

        name = name.strip()

        if not name:
            raise FieldEmptyError(field_name)

        if len(name) > CharacteristicGroupValidator.MAX_NAME_LENGTH:
            raise FieldMaxLengthError(field_name, CharacteristicGroupValidator.MAX_NAME_LENGTH)

    @staticmethod
    def validate_category_id(category_id: int) -> None:
        if category_id is None:
            raise FieldRequiredError("category_id")

        from catalog.models import Category
        if not Category.objects.filter(pk=category_id).exists():
            raise ObjectNotFoundError("Category", category_id)

    @staticmethod
    def validate_unique_name(name: str, category_id: int, group_id: int = None) -> None:
        from catalog.models import CharacteristicGroup
        from django.db.models import Q

        query = CharacteristicGroup.objects.filter(
            Q(name__iexact=name),
            Q(category_id=category_id)
        )
        if group_id:
            query = query.exclude(pk=group_id)

        if query.exists():
            raise ObjectAlreadyExistsError("CharacteristicGroup", "name", name)