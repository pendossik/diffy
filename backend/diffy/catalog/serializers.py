"""Сериализаторы приложения catalog."""
from rest_framework import serializers
from catalog.models import Category, Product, CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


class CategoryListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка категорий."""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра категории."""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


class CategoryCreateSerializer(serializers.Serializer):
    """Сериализатор для создания категории."""
    name = serializers.CharField(max_length=100)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название категории не может быть пустым")
        if len(value.strip()) > 100:
            raise serializers.ValidationError("Название категории не должно превышать 100 символов")
        return value.strip()

    def create(self, validated_data):
        return Category.objects.create(**validated_data)


class CategoryUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления категории."""
    name = serializers.CharField(max_length=100, required=False)

    def validate_name(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Название категории не может быть пустым")
            if len(value.strip()) > 100:
                raise serializers.ValidationError("Название категории не должно превышать 100 символов")
            return value.strip()
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка товаров."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category_id', 'category_name', 'img_url')
        read_only_fields = ('id', 'category_name')


class ProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра товара."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category_id', 'category_name', 'img_url')
        read_only_fields = ('id', 'category_name')


class ProductCreateSerializer(serializers.Serializer):
    """Сериализатор для создания товара."""
    name = serializers.CharField(max_length=200)
    category_id = serializers.IntegerField()
    img_url = serializers.CharField(max_length=300, required=False, allow_null=True, allow_blank=True)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара не может быть пустым")
        if len(value.strip()) > 200:
            raise serializers.ValidationError("Название товара не должно превышать 200 символов")
        return value.strip()

    def validate_category_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Категория с указанным ID не найдена")
        return value

    def validate_img_url(self, value):
        if value is not None and value.strip():
            if len(value) > 300:
                raise serializers.ValidationError("URL изображения не должен превышать 300 символов")
            return value.strip()
        return value


class ProductUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления товара."""
    name = serializers.CharField(max_length=200, required=False)
    category_id = serializers.IntegerField(required=False)
    img_url = serializers.CharField(max_length=300, required=False, allow_null=True, allow_blank=True)

    def validate_name(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Название товара не может быть пустым")
            if len(value.strip()) > 200:
                raise serializers.ValidationError("Название товара не должно превышать 200 символов")
            return value.strip()
        return value

    def validate_category_id(self, value):
        if value is not None and not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Категория с указанным ID не найдена")
        return value

    def validate_img_url(self, value):
        if value is not None and value.strip():
            if len(value) > 300:
                raise serializers.ValidationError("URL изображения не должен превышать 300 символов")
            return value.strip()
        return value


class CharacteristicGroupListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка групп характеристик."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CharacteristicGroup
        fields = ('id', 'name', 'category_id', 'category_name', 'order')
        read_only_fields = ('id', 'category_name')


class CharacteristicGroupDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра группы характеристик."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CharacteristicGroup
        fields = ('id', 'name', 'category_id', 'category_name', 'order')
        read_only_fields = ('id', 'category_name')


class CharacteristicGroupCreateSerializer(serializers.Serializer):
    """Сериализатор для создания группы характеристик."""
    name = serializers.CharField(max_length=100)
    category_id = serializers.IntegerField()
    order = serializers.IntegerField(required=False, default=0)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название группы не может быть пустым")
        if len(value.strip()) > 100:
            raise serializers.ValidationError("Название группы не должно превышать 100 символов")
        return value.strip()

    def validate_category_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Категория с указанным ID не найдена")
        return value


class CharacteristicGroupUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления группы характеристик."""
    name = serializers.CharField(max_length=100, required=False)
    category_id = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False)

    def validate_name(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Название группы не может быть пустым")
            if len(value.strip()) > 100:
                raise serializers.ValidationError("Название группы не должно превышать 100 символов")
            return value.strip()
        return value

    def validate_category_id(self, value):
        if value is not None and not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Категория с указанным ID не найдена")
        return value


class CharacteristicTemplateListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка шаблонов характеристик."""
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = CharacteristicTemplate
        fields = ('id', 'name', 'group_id', 'group_name', 'order')
        read_only_fields = ('id', 'group_name')


class CharacteristicTemplateDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра шаблона характеристик."""
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = CharacteristicTemplate
        fields = ('id', 'name', 'group_id', 'group_name', 'order')
        read_only_fields = ('id', 'group_name')


class CharacteristicTemplateCreateSerializer(serializers.Serializer):
    """Сериализатор для создания шаблона характеристик."""
    name = serializers.CharField(max_length=100)
    group_id = serializers.IntegerField()
    order = serializers.IntegerField(required=False, default=0)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название шаблона не может быть пустым")
        if len(value.strip()) > 100:
            raise serializers.ValidationError("Название шаблона не должно превышать 100 символов")
        return value.strip()

    def validate_group_id(self, value):
        if not CharacteristicGroup.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Группа характеристик с указанным ID не найдена")
        return value


class CharacteristicTemplateUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления шаблона характеристик."""
    name = serializers.CharField(max_length=100, required=False)
    group_id = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False)

    def validate_name(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Название шаблона не может быть пустым")
            if len(value.strip()) > 100:
                raise serializers.ValidationError("Название шаблона не должно превышать 100 символов")
            return value.strip()
        return value

    def validate_group_id(self, value):
        if value is not None and not CharacteristicGroup.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Группа характеристик с указанным ID не найдена")
        return value


class CharacteristicValueListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка значений характеристик."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = CharacteristicValue
        fields = ('id', 'product_id', 'product_name', 'template_id', 'template_name', 'value')
        read_only_fields = ('id', 'product_name', 'template_name')


class CharacteristicValueDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра значения характеристик."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = CharacteristicValue
        fields = ('id', 'product_id', 'product_name', 'template_id', 'template_name', 'value')
        read_only_fields = ('id', 'product_name', 'template_name')


class CharacteristicValueCreateSerializer(serializers.Serializer):
    """Сериализатор для создания значения характеристик."""
    product_id = serializers.IntegerField()
    template_id = serializers.IntegerField()
    value = serializers.CharField(max_length=500)

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Товар с указанным ID не найден")
        return value

    def validate_template_id(self, value):
        if not CharacteristicTemplate.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Шаблон характеристик с указанным ID не найден")
        return value

    def validate_value(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Значение характеристики не может быть пустым")
        if len(value.strip()) > 500:
            raise serializers.ValidationError("Значение характеристики не должно превышать 500 символов")
        return value.strip()


class CharacteristicValueUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления значения характеристик."""
    product_id = serializers.IntegerField(required=False)
    template_id = serializers.IntegerField(required=False)
    value = serializers.CharField(max_length=500, required=False)

    def validate_product_id(self, value):
        if value is not None and not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Товар с указанным ID не найден")
        return value

    def validate_template_id(self, value):
        if value is not None and not CharacteristicTemplate.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Шаблон характеристик с указанным ID не найден")
        return value

    def validate_value(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Значение характеристики не может быть пустым")
            if len(value.strip()) > 500:
                raise serializers.ValidationError("Значение характеристики не должно превышать 500 символов")
            return value.strip()
        return value