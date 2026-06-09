from rest_framework import serializers

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


class CompareRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=3,
        help_text="Список ID товаров для сравнения (от 1 до 3)"
    )
