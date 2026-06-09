from rest_framework.exceptions import ValidationError

from ..models import FavoriteComparison


class FavoriteComparisonService:
    @staticmethod
    def get_queryset_for_user(user):
        return FavoriteComparison.objects.filter(user=user).prefetch_related('products')

    @staticmethod
    def create_favorite(user, product_ids: list) -> FavoriteComparison:
        product_ids = sorted(product_ids)

        items_hash = f"{user.id}:" + ",".join(map(str, product_ids))

        if FavoriteComparison.objects.filter(products_hash=items_hash).exists():
            raise ValidationError({"detail": "Такое сравнение уже есть в избранном."})

        comparison = FavoriteComparison.objects.create(
            user=user,
            products_hash=items_hash
        )
        comparison.products.set(product_ids)
        return comparison
