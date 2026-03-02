from rest_framework import serializers
from .models import Category, Product

# только для отображения каталога, без характеристик
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    # Мы убираем SerializerMethodField, так как для списка товаров 
    # характеристики обычно не нужны или грузятся отдельно.
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'img']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# 1. Легкий сериализатор товара для превью в избранном
class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'img']
