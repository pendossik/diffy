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
    # Используем вложенный сериализатор для чтения
    product_1 = ProductSerializer(read_only=True)
    product_2 = ProductSerializer(read_only=True)
    
    # А для записи используем PrimaryKeyRelatedField (id)
    product_1_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product_1', write_only=True
    )
    product_2_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product_2', write_only=True
    )

    class Meta:
        model = FavoritePair
        fields = ["id", "product_1", "product_2", "product_1_id", "product_2_id", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, data):
        p1 = data['product_1']
        p2 = data['product_2']

        if p1 == p2:
            raise serializers.ValidationError("Нельзя добавить пару одинаковых товаров.")

        # Сортируем прямо здесь, чтобы в БД всегда летело (меньшее, большее)
        if p1.id > p2.id:
            p1, p2 = p2, p1
            data['product_1'] = p1
            data['product_2'] = p2

        # Проверка на уникальность вручную, т.к. мы могли поменять местами p1 и p2
        user = self.context['request'].user
        if FavoritePair.objects.filter(user=user, product_1=p1, product_2=p2).exists():
             raise serializers.ValidationError("Эта пара уже в избранном.")

        return data
    
    def create(self, validated_data):
        # Добавляем пользователя из контекста запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


