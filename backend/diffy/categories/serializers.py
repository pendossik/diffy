"""Сериализаторы приложения categories."""
from rest_framework import serializers
from .models import Category
from django.db import models


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения категории в списке.

    Возвращает названия на обоих языках для гибкости на фронтенде.
    """
    # Явно указываем поля переводов для читаемости в схеме
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'name_ru', 'name_en')
        ref_name = 'CategoryList'

    def to_representation(self, instance):
        """
        Добавить текущее название в зависимости от языка запроса.

        Фронтенд может использовать либо 'name' (авто-определение),
        либо явно 'name_ru'/'name_en'.
        """
        data = super().to_representation(instance)
        # 'name' уже содержит значение для текущей локали благодаря modeltranslation
        return data


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра категории."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'name_ru', 'name_en')
        read_only_fields = fields
        ref_name = 'CategoryDetail'


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания категории.

    Принимает name (для текущего языка) и опционально name_en/name_ru.
    """
    name_ru = serializers.CharField(required=False, allow_blank=True, max_length=100)
    name_en = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = Category
        fields = ('name', 'name_ru', 'name_en')
        ref_name = 'CategoryCreate'

    def validate_name(self, value):
        """Проверить уникальность имени в обоих языках и длину."""
        value_clean = value.strip().capitalize()
        
        # Валидация длины (HIGH #2)
        if len(value_clean) > 100:
            raise serializers.ValidationError("Название категории не должно превышать 100 символов")
        
        if not value_clean:
            raise serializers.ValidationError("Название категории не может быть пустым")
        
        # Проверяем коллизии в любом из языковых полей
        if Category.objects.filter(
            models.Q(name_ru__iexact=value_clean) |
            models.Q(name_en__iexact=value_clean)
        ).exists():
            raise serializers.ValidationError("Категория с таким именем уже существует")
        return value_clean

    def create(self, validated_data):
        """
        Создать категорию, заполняя переводы.

        Если перевод не указан — копируем основное название.
        """
        name_clean = validated_data['name'].strip().capitalize()
        name_ru = validated_data.get('name_ru', '').strip() or name_clean
        name_en = validated_data.get('name_en', '').strip() or name_clean

        return Category.objects.create(
            name=name_clean,
            name_ru=name_ru,
            name_en=name_en
        )

class CategoryUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления категории."""
    name_ru = serializers.CharField(required=False, allow_blank=True, max_length=100)
    name_en = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = Category
        fields = ('name', 'name_ru', 'name_en')
        ref_name = 'CategoryUpdate'

    def validate_name(self, value):
        """Проверить уникальность, исключая текущий объект."""
        value_clean = value.strip().capitalize()
        
        # Валидация длины (HIGH #2)
        if len(value_clean) > 100:
            raise serializers.ValidationError("Название категории не должно превышать 100 символов")
        
        if not value_clean:
            raise serializers.ValidationError("Название категории не может быть пустым")
        
        # Проверяем коллизии в любом из языковых полей
        if Category.objects.filter(
            models.Q(name_ru__iexact=value_clean) |
            models.Q(name_en__iexact=value_clean)
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Категория с таким именем уже существует")
        return value_clean

    def update(self, instance, validated_data):
        """Обновить поля, сохраняя существующие переводы при отсутствии новых."""
        instance.name = validated_data.get('name', instance.name).strip().capitalize()
        instance.name_ru = validated_data.get('name_ru', '').strip() or instance.name_ru or instance.name
        instance.name_en = validated_data.get('name_en', '').strip() or instance.name_en or instance.name
        instance.save()
        return instance


class CategorySearchSerializer(serializers.Serializer):
    """Сериализатор для поискового запроса."""
    search = serializers.CharField(
        max_length=100,
        min_length=2,  # MEDIUM #3: Минимальная длина поиска
        required=False,
        allow_blank=True,
        help_text="Поисковая подстрока (мин. 2 символа, ищет по name_ru и name_en)"
    )

    class Meta:
        ref_name = 'CategorySearch'