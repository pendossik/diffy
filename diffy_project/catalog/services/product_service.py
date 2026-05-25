# catalog/services/product_service.py

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from ..models import Category, Product, CharacteristicGroup, CharacteristicValue

class ProductService:
    
    @staticmethod
    @transaction.atomic
    def create_product_with_characteristics(validated_data: dict) -> Product:
        """
        Сервис для создания товара и его характеристик на основе словаря данных.
        Все происходит в одной транзакции.
        """
        category_name = validated_data.get('category')
        name = validated_data.get('name')
        img = validated_data.get('img', '')
        groups_data = validated_data.get('characteristics_groups', [])

        # 1. Проверка категории
        try:
            category_obj = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            # Выбрасываем DRF ValidationError, чтобы API автоматически вернуло 400 статус
            raise ValidationError({"category": f"Категория '{category_name}' не найдена в базе."})

        # 2. Подгружаем все группы и шаблоны этой категории для быстрой проверки
        valid_structure = {}
        groups = CharacteristicGroup.objects.filter(category=category_obj).prefetch_related('templates')
        for group in groups:
            valid_structure[group.name.lower()] = {
                template.name.lower(): template for template in group.templates.all()
            }

        # 3. Создаем сам товар (если будет ошибка дальше, транзакция откатит это действие)
        product = Product.objects.create(name=name, category=category_obj, img=img)

        # 4. Проверяем присланные группы и собираем значения для массового создания
        values_to_create = []
        
        # +++ ДОБАВЛЯЕМ МНОЖЕСТВО ДЛЯ ОТСЛЕЖИВАНИЯ ДУБЛИКАТОВ +++
        seen_templates = set()
        
        for group_data in groups_data:
            group_name_lower = group_data['name'].lower()
            
            if group_name_lower not in valid_structure:
                raise ValidationError(
                    {"characteristics_groups": f"Группа '{group_data['name']}' не привязана к категории '{category_name}'."}
                )
            
            valid_templates_for_group = valid_structure[group_name_lower]
            
            for char_data in group_data['characteristics']:
                char_name_lower = char_data['name'].lower()
                
                if char_name_lower not in valid_templates_for_group:
                    raise ValidationError(
                        {"characteristics_groups": f"Характеристика '{char_data['name']}' не найдена в группе '{group_data['name']}'."}
                    )
                
                # Получаем сам объект шаблона
                template_obj = valid_templates_for_group[char_name_lower]

                # Проверем на дубликаты чтобы unique_together = ('product', 'template') в CharacteristicValue
                # не ругался (обрабатываем ошибку на стороне сервера для понятного вывода ошибки)
                if template_obj.id in seen_templates:
                    raise ValidationError(
                        {"characteristics_groups": f"Дублирование характеристики '{char_data['name']}'! Уберите повторы из запроса."}
                    )
                
                # Запоминаем, что мы уже добавили эту характеристику товару
                seen_templates.add(template_obj.id)

                # Добавляем в список для создания
                values_to_create.append(
                    CharacteristicValue(
                        product=product,
                        template=template_obj,
                        value=char_data['value']
                    )
                )

        # 5. Массово сохраняем в БД (очень быстро)
        if values_to_create:
            CharacteristicValue.objects.bulk_create(values_to_create)

        return product

    @staticmethod
    def delete_product(product_id: int):
        """Удаление товара (с каскадным удалением характеристик)"""
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise NotFound("Товар не найден")
        
        product.delete()