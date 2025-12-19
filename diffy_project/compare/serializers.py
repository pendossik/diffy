from rest_framework import serializers
from .models import Category, Product, FavoritePair, CharacteristicGroup, CharacteristicValue
# для свагера
from drf_spectacular.utils import extend_schema_field



# class CharacteristicValueSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='template.name', read_only=True)
    
#     class Meta:
#         model = CharacteristicValue
#         fields = ['id', 'name', 'value']

# class CharacteristicGroupSerializer(serializers.ModelSerializer):
#     characteristics = serializers.SerializerMethodField()

#     class Meta:
#         model = CharacteristicGroup
#         fields = ['name', 'characteristics']

#     # Подсказываем Swagger, что тут вернется список CharacteristicValueSerializer
#     @extend_schema_field(CharacteristicValueSerializer(many=True))
#     def get_characteristics(self, group):
#         # Возвращаем только характеристики текущего продукта
#         product = self.context.get('product')
#         if not product:
#             return []
#         values = CharacteristicValue.objects.filter(product=product, template__group=group)
#         return CharacteristicValueSerializer(values, many=True).data

# class DetailedProductSerializer(serializers.ModelSerializer):
#     """Полный объект товара с вложенными характеристиками"""
#     category = serializers.CharField(source='category.name')
#     # Явно указываем сериализатор для групп, чтобы Swagger не писал "string"
#     characteristics_groups = CharacteristicGroupSerializer(many=True)
#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'category', 'img', 'characteristics_groups']

# только для отображения каталога, без характеристик
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    # Мы убираем SerializerMethodField, так как для списка товаров 
    # характеристики обычно не нужны или грузятся отдельно.
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'img']

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

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

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


