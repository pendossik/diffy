from catalog.validators.exceptions import (
    FieldRequiredError,
    FieldMaxLengthError,
    FieldEmptyError,
    ObjectAlreadyExistsError,
)


class CategoryValidator:
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

        if len(name) > CategoryValidator.MAX_NAME_LENGTH:
            raise FieldMaxLengthError(field_name, CategoryValidator.MAX_NAME_LENGTH)

    @staticmethod
    def validate_unique_name(name: str, category_id: int = None) -> None:
        from catalog.models import Category
        from django.db.models import Q

        query = Category.objects.filter(Q(name__iexact=name))
        if category_id:
            query = query.exclude(pk=category_id)

        if query.exists():
            raise ObjectAlreadyExistsError("Category", "name", name)