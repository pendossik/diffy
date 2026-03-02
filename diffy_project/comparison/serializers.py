from rest_framework import serializers
from .models import Product, FavoriteComparison
from catalog.serializers import ProductShortSerializer

"""
    Хотя эти сериализаторы описывают данные характеристик,
    они являются частью логики сравнения. Они определяют, в каком именно формате
    фронтенд получит результат сопоставления товаров.
"""
class CharacteristicItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID значения или шаблона")
    name = serializers.CharField(help_text="Название характеристики (н-р, 'Вес')")
    value = serializers.CharField(help_text="Значение (н-р, '1.5 кг')")

class CharsGroupSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Название группы (н-р, 'Корпус')")
    characteristics = CharacteristicItemSerializer(many=True)


class CompareResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    img = serializers.CharField()
    characteristics_groups = CharsGroupSerializer(many=True)


# Сериализатор для входных данных сравнения
class CompareRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=3,
        help_text="Список ID товаров для сравнения (от 1 до 3)"
    )


# 2. Основной сериализатор избранного
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

    def create(self, validated_data):
        user = self.context['request'].user
        product_ids = sorted(validated_data.pop('product_ids'))
        
        # Генерируем уникальный ключ для набора (чтобы не было дублей у одного юзера)
        # Формат: "user_id:1,2,3"
        items_hash = f"{user.id}:" + ",".join(map(str, product_ids))
        
        if FavoriteComparison.objects.filter(products_hash=items_hash).exists():
            raise serializers.ValidationError({"detail": "Такое сравнение уже есть в избранном."})

        # Создаем запись
        comparison = FavoriteComparison.objects.create(
            user=user, 
            products_hash=items_hash
        )
        # Привязываем товары
        comparison.products.set(product_ids)
        return comparison
