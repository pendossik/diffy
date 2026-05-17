from rest_framework import serializers

class AICompareRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=3, # Ограничим до 3
        help_text="ID товаров для AI сравнения"
    )
    
class AICompareResponseSerializer(serializers.Serializer):
    summary = serializers.CharField(help_text="Ответ нейросети в формате Markdown")