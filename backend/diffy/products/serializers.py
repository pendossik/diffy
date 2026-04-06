"""Сериализаторы приложения products."""
from rest_framework import serializers
from .models import Product
from categories.serializers import CategoryListSerializer
from django.utils import translation
from django.db import models


class ProductListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения товара в списке.
    
    Возвращает названия на обоих языках и информацию о категории.
    """
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    category_info = CategoryListSerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'name_ru', 'name_en', 'category', 'category_info', 'img')
        ref_name = 'ProductList'
    
    def to_representation(self, instance):
        """Добавить текущее название в зависимости от языка запроса."""
        data = super().to_representation(instance)
        return data


class ProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра товара."""
    name_ru = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    category_info = CategoryListSerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'name_ru', 'name_en', 'category', 'category_info', 'img')
        read_only_fields = fields
        ref_name = 'ProductDetail'


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания товара.
    
    Принимает name (для текущего языка) и опционально name_en/name_ru.
    """
    name_ru = serializers.CharField(required=False, allow_blank=True)
    name_en = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Product
        fields = ('name', 'name_ru', 'name_en', 'category', 'img')
        ref_name = 'ProductCreate'
    
    def validate_name(self, value):
        """Проверить уникальность имени в рамках категории."""
        value_clean = value.strip()
        category_id = self.initial_data.get('category')
        
        if category_id:
            # Проверяем коллизии в любом из языковых полей в рамках категории
            if Product.objects.filter(
                category_id=category_id
            ).filter(
                models.Q(name_ru__iexact=value_clean) | 
                models.Q(name_en__iexact=value_clean)
            ).exists():
                raise serializers.ValidationError(
                    "Товар с таким именем уже существует в этой категории"
                )
        return value_clean
    
    def validate_img(self, value):
        """Валидация пути к изображению."""
        if value and not value.startswith('products/'):
            raise serializers.ValidationError(
                "Путь к изображению должен начинаться с 'products/'"
            )
        return value
    
    def create(self, validated_data):
        """
        Создать товар, корректно заполняя все языковые поля.
        """
        # Извлекаем переводы из validated_data
        name = validated_data.pop('name', None)
        name_ru = validated_data.pop('name_ru', None)
        name_en = validated_data.pop('name_en', None)
        
        # Если переводы не указаны, используем name как fallback
        if name_ru is None or name_ru == '':
            name_ru = name
        if name_en is None or name_en == '':
            name_en = name
        
        # Если name не указан, используем name_ru (для текущей локали)
        if name is None or name == '':
            name = name_ru
        
        # Создаем объект БЕЗ передачи name (чтобы modeltranslation не вмешивался)
        product = Product(
            name_ru=name_ru,
            name_en=name_en,
            **validated_data  # category, img
        )
        
        # Явно устанавливаем name для текущей локали
        # (это важно для корректной работы modeltranslation)
        from django.utils import translation
        current_lang = translation.get_language()
        
        if current_lang == 'ru':
            product.name = name_ru
        elif current_lang == 'en':
            product.name = name_en
        else:
            product.name = name_ru  # fallback на русский
        
        product.save()
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления товара.
    
    Все поля необязательные для поддержки PATCH запросов.
    """
    name = serializers.CharField(required=False, allow_blank=True)
    name_ru = serializers.CharField(required=False, allow_blank=True)
    name_en = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    img = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = ('name', 'name_ru', 'name_en', 'category', 'img')
        ref_name = 'ProductUpdate'

    def validate_name(self, value):
        """Проверить уникальность и валидность имени."""
        # Разрешаем None (поле не передано)
        if value is None:
            return value
            
        value_clean = value.strip()
        
        # Проверяем пустое имя
        if not value_clean:
            raise serializers.ValidationError("Название товара не может быть пустым")
            
        # Проверяем длину
        if len(value_clean) > 200:
            raise serializers.ValidationError("Название товара не должно превышать 200 символов")
            
        category_id = self.initial_data.get('category', self.instance.category_id)

        if Product.objects.filter(
            category_id=category_id
        ).filter(
            models.Q(name_ru__iexact=value_clean) |
            models.Q(name_en__iexact=value_clean)
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                "Товар с таким именем уже существует в этой категории"
            )
        return value_clean

    def validate_img(self, value):
        """Валидация пути к изображению."""
        if value and not value.startswith('products/'):
            raise serializers.ValidationError(
                "Путь к изображению должен начинаться с 'products/'"
            )
        return value

    def update(self, instance, validated_data):
        """Обновить только указанные поля, сохраняя существующие при отсутствии новых."""
        # Обновляем только если поле передано
        if 'name' in validated_data:
            name = validated_data['name'].strip() if validated_data['name'] else ''
            if name:
                instance.name = name
            elif 'name_ru' not in validated_data and 'name_en' not in validated_data:
                # Если name пустой и переводы не указаны — оставляем как есть
                pass
                
        if 'name_ru' in validated_data:
            name_ru = validated_data['name_ru'].strip() if validated_data['name_ru'] else ''
            instance.name_ru = name_ru or instance.name_ru
            
        if 'name_en' in validated_data:
            name_en = validated_data['name_en'].strip() if validated_data['name_en'] else ''
            instance.name_en = name_en or instance.name_en
            
        if 'category' in validated_data:
            from categories.models import Category
            instance.category = Category.objects.get(pk=validated_data['category'])
            
        if 'img' in validated_data:
            instance.img = validated_data['img']
            
        instance.save()
        return instance


class ProductSearchSerializer(serializers.Serializer):
    """Сериализатор для поискового запроса."""
    search = serializers.CharField(
        max_length=200,
        min_length=2,  # MEDIUM: Минимальная длина поиска
        required=False,
        allow_blank=True,
        help_text="Поисковая подстрока (мин. 2 символа, ищет по name_ru и name_en)"
    )
    category = serializers.IntegerField(
        required=False,
        help_text="Фильтр по ID категории"
    )

    class Meta:
        ref_name = 'ProductSearch'