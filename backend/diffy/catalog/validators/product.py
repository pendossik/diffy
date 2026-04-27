from catalog.validators.exceptions import (
    FieldRequiredError,
    FieldMaxLengthError,
    FieldEmptyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)


class ProductValidator:
    MAX_NAME_LENGTH = 200
    MAX_IMG_URL_LENGTH = 300

    @staticmethod
    def validate_name(name: str, field_name: str = "name") -> None:
        if name is None:
            raise FieldRequiredError(field_name)

        if not isinstance(name, str):
            name = str(name)

        name = name.strip()

        if not name:
            raise FieldEmptyError(field_name)

        if len(name) > ProductValidator.MAX_NAME_LENGTH:
            raise FieldMaxLengthError(field_name, ProductValidator.MAX_NAME_LENGTH)

    @staticmethod
    def validate_category_id(category_id: int) -> None:
        if category_id is None:
            raise FieldRequiredError("category_id")

        from catalog.models import Category
        if not Category.objects.filter(pk=category_id).exists():
            raise ObjectNotFoundError("Category", category_id)

    @staticmethod
    def validate_unique_name(name: str, category_id: int, product_id: int = None) -> None:
        from catalog.models import Product
        from django.db.models import Q

        query = Product.objects.filter(
            Q(name__iexact=name),
            Q(category_id=category_id)
        )
        if product_id:
            query = query.exclude(pk=product_id)

        if query.exists():
            raise ObjectAlreadyExistsError("Product", "name", name)

    @staticmethod
    def validate_img_url(img_url: str) -> None:
        if img_url is None:
            return

        if not isinstance(img_url, str):
            img_url = str(img_url)

        img_url = img_url.strip()
        if img_url and len(img_url) > ProductValidator.MAX_IMG_URL_LENGTH:
            raise FieldMaxLengthError("img_url", ProductValidator.MAX_IMG_URL_LENGTH)