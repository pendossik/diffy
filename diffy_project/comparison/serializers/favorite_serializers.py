from rest_framework import serializers

from ..models import FavoriteComparison
from catalog.models import Product
from catalog.serializers.product_serializers import ProductShortSerializer


class FavoriteComparisonSerializer(serializers.ModelSerializer):
    # Для чтения: возвращаем список товаров с короткими данными
    products = ProductShortSerializer(many=True, read_only=True)

    # Для записи: принимаем список ID
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        min_length=1,
        max_length=3,
        help_text="Список ID товаров для сохранения (1-3 шт)"
    )

    class Meta:
        model = FavoriteComparison
        fields = ['id', 'products', 'product_ids', 'created_at']
        read_only_fields = ['created_at']

    def validate_product_ids(self, ids):
        # Проверяем существование товаров
        if Product.objects.filter(id__in=ids).count() != len(ids):
            raise serializers.ValidationError("Один или несколько товаров не найдены.")
        return ids
