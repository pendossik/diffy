from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# сериализвторы для создания категории и её характеристик
class TemplateCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, help_text="Название характеристики")
    order = serializers.IntegerField(default=0)

class GroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, help_text="Название группы")
    order = serializers.IntegerField(default=0)
    templates = TemplateCreateSerializer(many=True)

class CategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    char_groups = GroupCreateSerializer(many=True)

    def validate(self, data):
        """
        Проверка на отсутствие дубликатов групп и характеристик 
        внутри тела одного запроса.
        """
        groups = data.get('char_groups', [])
        group_names = set()
        
        for g in groups:
            if g['name'] in group_names:
                raise serializers.ValidationError(f"Дублируется группа характеристик: {g['name']}")
            group_names.add(g['name'])
            
            template_names = set()
            for t in g.get('templates', []):
                if t['name'] in template_names:
                    raise serializers.ValidationError(
                        f"Дублируется шаблон '{t['name']}' в группе '{g['name']}'"
                    )
                template_names.add(t['name'])
                
        return data