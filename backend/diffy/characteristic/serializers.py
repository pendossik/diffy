"""Сериализаторы приложения characteristic."""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue
from categories.models import Category
from products.models import Product


# =============================================================================
# CharacteristicGroup Serializers
# =============================================================================

class CharacteristicGroupListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения группы характеристик в списке."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    category_info = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicGroup
        fields = ('id', 'name', 'name_ru', 'name_en', 'category', 'category_info', 'order')
        ref_name = 'CharacteristicGroupList'

    @extend_schema_field(dict)
    def get_category_info(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'name_ru': obj.category.name_ru,
            'name_en': obj.category.name_en
        }


class CharacteristicGroupDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра группы характеристик."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    category_info = serializers.SerializerMethodField()
    templates = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicGroup
        fields = ('id', 'name', 'name_ru', 'name_en', 'category', 'category_info', 'order', 'templates')
        read_only_fields = fields
        ref_name = 'CharacteristicGroupDetail'

    @extend_schema_field(dict)
    def get_category_info(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'name_ru': obj.category.name_ru,
            'name_en': obj.category.name_en
        }

    @extend_schema_field(list)
    def get_templates(self, obj):
        templates = obj.templates.all()
        return [
            {
                'id': t.id,
                'name': t.name,
                'name_ru': t.name_ru,
                'name_en': t.name_en,
                'order': t.order
            }
            for t in templates
        ]


class CharacteristicGroupCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания группы характеристик."""
    name_ru = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200, default=None)
    name_en = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200, default=None)
    category = serializers.IntegerField(required=True)

    class Meta:
        model = CharacteristicGroup
        fields = ('name', 'name_ru', 'name_en', 'category', 'order')
        ref_name = 'CharacteristicGroupCreate'

    def validate_name(self, value):
        """Проверить уникальность имени в категории."""
        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Название группы не может быть пустым")
        return value_clean

    def create(self, validated_data):
        """Создать группу, заполняя переводы."""
        name = validated_data.pop('name', None)
        name_ru = validated_data.pop('name_ru', None)
        if not name_ru:
            name_ru = name
        name_en = validated_data.pop('name_en', None)
        if not name_en:
            name_en = name
        category_id = validated_data.pop('category')
        order = validated_data.pop('order', 0)

        group = CharacteristicGroup(
            category_id=category_id,
            name=name,
            name_ru=name_ru,
            name_en=name_en,
            order=order
        )
        group.save()
        return group


class CharacteristicGroupUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления группы характеристик."""
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    name_ru = serializers.CharField(required=False, allow_blank=True, max_length=200)
    name_en = serializers.CharField(required=False, allow_blank=True, max_length=200)
    order = serializers.IntegerField(required=False)

    class Meta:
        model = CharacteristicGroup
        fields = ('name', 'name_ru', 'name_en', 'order')
        ref_name = 'CharacteristicGroupUpdate'

    def validate_name(self, value):
        """Проверить уникальность и валидность имени."""
        if value is None:
            return value

        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Название группы не может быть пустым")
        return value_clean

    def update(self, instance, validated_data):
        """Обновить только указанные поля."""
        if 'name' in validated_data:
            instance.name = validated_data['name'].strip()
        if 'name_ru' in validated_data:
            instance.name_ru = validated_data['name_ru'].strip() or instance.name_ru
        if 'name_en' in validated_data:
            instance.name_en = validated_data['name_en'].strip() or instance.name_en
        if 'order' in validated_data:
            instance.order = validated_data['order']
        instance.save()
        return instance


# =============================================================================
# CharacteristicTemplate Serializers
# =============================================================================

class CharacteristicTemplateListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения шаблона характеристики в списке."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    group_info = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicTemplate
        fields = ('id', 'name', 'name_ru', 'name_en', 'group', 'group_info', 'order')
        ref_name = 'CharacteristicTemplateList'

    @extend_schema_field(dict)
    def get_group_info(self, obj):
        return {
            'id': obj.group.id,
            'name': obj.group.name,
            'name_ru': obj.group.name_ru,
            'name_en': obj.group.name_en
        }


class CharacteristicTemplateDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра шаблона характеристики."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    group_info = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicTemplate
        fields = ('id', 'name', 'name_ru', 'name_en', 'group', 'group_info', 'order')
        read_only_fields = fields
        ref_name = 'CharacteristicTemplateDetail'

    @extend_schema_field(dict)
    def get_group_info(self, obj):
        return {
            'id': obj.group.id,
            'name': obj.group.name,
            'name_ru': obj.group.name_ru,
            'name_en': obj.group.name_en
        }


class CharacteristicTemplateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания шаблона характеристики."""
    name_ru = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200, default=None)
    name_en = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200, default=None)
    group = serializers.IntegerField(required=True)

    class Meta:
        model = CharacteristicTemplate
        fields = ('name', 'name_ru', 'name_en', 'group', 'order')
        ref_name = 'CharacteristicTemplateCreate'

    def validate_name(self, value):
        """Проверить уникальность имени в группе."""
        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Название характеристики не может быть пустым")
        return value_clean

    def create(self, validated_data):
        """Создать шаблон, заполняя переводы."""
        name = validated_data.pop('name', None)
        name_ru = validated_data.pop('name_ru', None)
        if not name_ru:
            name_ru = name
        name_en = validated_data.pop('name_en', None)
        if not name_en:
            name_en = name
        group_id = validated_data.pop('group')
        order = validated_data.pop('order', 0)

        template = CharacteristicTemplate(
            group_id=group_id,
            name=name,
            name_ru=name_ru,
            name_en=name_en,
            order=order
        )
        template.save()
        return template


class CharacteristicTemplateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления шаблона характеристики."""
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    name_ru = serializers.CharField(required=False, allow_blank=True, max_length=200)
    name_en = serializers.CharField(required=False, allow_blank=True, max_length=200)
    order = serializers.IntegerField(required=False)

    class Meta:
        model = CharacteristicTemplate
        fields = ('name', 'name_ru', 'name_en', 'order')
        ref_name = 'CharacteristicTemplateUpdate'

    def validate_name(self, value):
        """Проверить уникальность и валидность имени."""
        if value is None:
            return value

        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Название характеристики не может быть пустым")
        return value_clean

    def update(self, instance, validated_data):
        """Обновить только указанные поля."""
        if 'name' in validated_data:
            instance.name = validated_data['name'].strip()
        if 'name_ru' in validated_data:
            instance.name_ru = validated_data['name_ru'].strip() or instance.name_ru
        if 'name_en' in validated_data:
            instance.name_en = validated_data['name_en'].strip() or instance.name_en
        if 'order' in validated_data:
            instance.order = validated_data['order']
        instance.save()
        return instance


# =============================================================================
# CharacteristicValue Serializers
# =============================================================================

class CharacteristicValueListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения значения характеристики в списке."""
    value_ru = serializers.CharField(read_only=True)
    value_en = serializers.CharField(read_only=True)
    template_info = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicValue
        fields = ('id', 'value', 'value_ru', 'value_en', 'template', 'template_info', 'product', 'product_info')
        ref_name = 'CharacteristicValueList'

    @extend_schema_field(dict)
    def get_template_info(self, obj):
        return {
            'id': obj.template.id,
            'name': obj.template.name,
            'name_ru': obj.template.name_ru,
            'name_en': obj.template.name_en,
            'group': {
                'id': obj.template.group.id,
                'name': obj.template.group.name,
                'name_ru': obj.template.group.name_ru,
                'name_en': obj.template.group.name_en
            }
        }

    @extend_schema_field(dict)
    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'name_ru': obj.product.name_ru,
            'name_en': obj.product.name_en
        }


class CharacteristicValueDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра значения характеристики."""
    value_ru = serializers.CharField(read_only=True)
    value_en = serializers.CharField(read_only=True)
    template_info = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = CharacteristicValue
        fields = ('id', 'value', 'value_ru', 'value_en', 'template', 'template_info', 'product', 'product_info')
        read_only_fields = fields
        ref_name = 'CharacteristicValueDetail'

    @extend_schema_field(dict)
    def get_template_info(self, obj):
        return {
            'id': obj.template.id,
            'name': obj.template.name,
            'name_ru': obj.template.name_ru,
            'name_en': obj.template.name_en,
            'group': {
                'id': obj.template.group.id,
                'name': obj.template.group.name,
                'name_ru': obj.template.group.name_ru,
                'name_en': obj.template.group.name_en
            }
        }

    @extend_schema_field(dict)
    def get_product_info(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'name_ru': obj.product.name_ru,
            'name_en': obj.product.name_en
        }


class CharacteristicValueCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания значения характеристики."""
    value_ru = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    value_en = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    product = serializers.IntegerField(required=True)
    template = serializers.IntegerField(required=True)

    class Meta:
        model = CharacteristicValue
        fields = ('value', 'value_ru', 'value_en', 'product', 'template')
        ref_name = 'CharacteristicValueCreate'

    def validate_value(self, value):
        """Проверить валидность значения."""
        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Значение характеристики не может быть пустым")
        return value_clean

    def create(self, validated_data):
        """Создать значение характеристики."""
        value = validated_data.pop('value', None)
        value_ru = validated_data.pop('value_ru', None) or value
        value_en = validated_data.pop('value_en', None) or value
        product_id = validated_data.pop('product')
        template_id = validated_data.pop('template')

        char_value = CharacteristicValue(
            product_id=product_id,
            template_id=template_id,
            value=value,
            value_ru=value_ru,
            value_en=value_en
        )
        char_value.save()
        return char_value


class CharacteristicValueUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления значения характеристики."""
    value = serializers.CharField(required=False, allow_blank=True, max_length=200)
    value_ru = serializers.CharField(required=False, allow_blank=True, max_length=200)
    value_en = serializers.CharField(required=False, allow_blank=True, max_length=200)

    class Meta:
        model = CharacteristicValue
        fields = ('value', 'value_ru', 'value_en')
        ref_name = 'CharacteristicValueUpdate'

    def validate_value(self, value):
        """Проверить валидность значения."""
        if value is None:
            return value

        value_clean = value.strip()
        if not value_clean:
            raise serializers.ValidationError("Значение характеристики не может быть пустым")
        return value_clean

    def update(self, instance, validated_data):
        """Обновить только указанные поля."""
        if 'value' in validated_data:
            instance.value = validated_data['value'].strip()
        if 'value_ru' in validated_data:
            instance.value_ru = validated_data['value_ru'].strip() or instance.value_ru
        if 'value_en' in validated_data:
            instance.value_en = validated_data['value_en'].strip() or instance.value_en
        instance.save()
        return instance
