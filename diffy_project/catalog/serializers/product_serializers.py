from rest_framework import serializers
from ..models import Product

# только для отображения каталога, без характеристик
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    # Мы убираем SerializerMethodField, так как для списка товаров 
    # характеристики обычно не нужны или грузятся отдельно.
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'img']


# легкий сериализатор товара для превью в избранном
class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'img']

# сериализоторы для создания товара админом
class FastCharacteristicSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Название характеристики (н-р, 'Вес')")
    value = serializers.CharField(help_text="Значение на русском (н-р, '233 г')")
    value_en = serializers.CharField(
        required=False, 
        allow_blank=True, 
        default=None, 
        help_text="Значение на английском (н-р, '233 g') — необязательно"
    )

class FastCharGroupSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Название группы (н-р, 'Корпус')")
    characteristics = FastCharacteristicSerializer(many=True)

class ProductFastCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, help_text="Наименование товара")
    category = serializers.CharField(help_text="Название категории, например 'Смартфоны'")
    img = serializers.CharField(max_length=300, required=False, allow_blank=True, help_text="Ссылка на фото")
    
    characteristics_groups = FastCharGroupSerializer(many=True)