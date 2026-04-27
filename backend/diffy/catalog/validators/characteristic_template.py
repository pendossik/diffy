from catalog.validators.exceptions import (
    FieldRequiredError,
    FieldMaxLengthError,
    FieldEmptyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)


class CharacteristicTemplateValidator:
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

        if len(name) > CharacteristicTemplateValidator.MAX_NAME_LENGTH:
            raise FieldMaxLengthError(field_name, CharacteristicTemplateValidator.MAX_NAME_LENGTH)

    @staticmethod
    def validate_group_id(group_id: int) -> None:
        if group_id is None:
            raise FieldRequiredError("group_id")

        from catalog.models import CharacteristicGroup
        if not CharacteristicGroup.objects.filter(pk=group_id).exists():
            raise ObjectNotFoundError("CharacteristicGroup", group_id)

    @staticmethod
    def validate_unique_name(name: str, group_id: int, template_id: int = None) -> None:
        from catalog.models import CharacteristicTemplate
        from django.db.models import Q

        query = CharacteristicTemplate.objects.filter(
            Q(name__iexact=name),
            Q(group_id=group_id)
        )
        if template_id:
            query = query.exclude(pk=template_id)

        if query.exists():
            raise ObjectAlreadyExistsError("CharacteristicTemplate", "name", name)