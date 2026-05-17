from rest_framework import serializers

class FastCharacteristicSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Название характеристики (н-р, 'Вес')")
    value = serializers.CharField(help_text="Значение (н-р, '233 г')")

class FastCharGroupSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Название группы (н-р, 'Корпус')")
    characteristics = FastCharacteristicSerializer(many=True)

class ProductFastCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, help_text="Наименование товара")
    category = serializers.CharField(help_text="Название категории, например 'Смартфоны'")
    img = serializers.CharField(max_length=300, required=False, allow_blank=True, help_text="Ссылка на фото")
    
    characteristics_groups = FastCharGroupSerializer(many=True)