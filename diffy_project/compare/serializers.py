from rest_framework import serializers
from .models import Category, Product, Characteristic, FavoritePair


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['id', 'name', 'value']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    characteristics = CharacteristicSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'characteristics']


class FavoritePairSerializer(serializers.ModelSerializer):
    product_1 = ProductSerializer()
    product_2 = ProductSerializer()

    class Meta:
        model = FavoritePair
        fields = ["id", "product_1", "product_2", "created_at"]


class FavoritePairCreateSerializer(serializers.Serializer):
    product_1 = serializers.IntegerField()
    product_2 = serializers.IntegerField()

    def validate(self, data):
        if data["product_1"] == data["product_2"]:
            raise serializers.ValidationError("Нельзя добавить пару одинаковых товаров.")
        return data


