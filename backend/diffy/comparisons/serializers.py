"""Сериализаторы приложения comparisons."""
from rest_framework import serializers
from .models import FavoriteComparison
from products.serializers import ProductListSerializer
from typing import List, Dict


class FavoriteComparisonListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка избранных сравнений.

    Возвращает краткую информацию о сравнении.
    """
    products_count = serializers.SerializerMethodField()
    products_preview = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteComparison
        fields = (
            'id',
            'products_count',
            'products_preview',
            'created_at',
        )
        ref_name = 'FavoriteComparisonList'

    def get_products_count(self, obj) -> int:
        """Получить количество товаров в сравнении."""
        return obj.products.count()

    def get_products_preview(self, obj) -> List[Dict]:
        """Получить превью товаров (первые 3)."""
        products = obj.products.all()[:3]
        return ProductListSerializer(products, many=True).data


class FavoriteComparisonDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о сравнении.

    Возвращает полную информацию о всех товарах в сравнении.
    """
    products = ProductListSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteComparison
        fields = (
            'id',
            'products',
            'products_count',
            'created_at',
        )
        ref_name = 'FavoriteComparisonDetail'

    def get_products_count(self, obj) -> int:
        """Получить количество товаров в сравнении."""
        return obj.products.count()


class FavoriteComparisonCreateSerializer(serializers.Serializer):
    """
    Сериализатор для добавления сравнения в избранное.

    Принимает список ID товаров.
    """
    product_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=2,
        required=True,
        help_text="Список ID товаров для сравнения (минимум 2)"
    )

    class Meta:
        ref_name = 'FavoriteComparisonCreate'

    def validate_product_ids(self, value):
        """Проверить что ID уникальны."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("ID товаров должны быть уникальны")
        return value
