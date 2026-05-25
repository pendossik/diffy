from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from ..models import Category, CharacteristicGroup, CharacteristicTemplate, Product

class CategoryService:
    @staticmethod
    @transaction.atomic  # Если где-то упадет ошибка, в БД ничего не запишется
    def create_category_with_hierarchy(validated_data: dict) -> Category:
        # 1. Создаем категорию
        category = Category.objects.create(name=validated_data['name'])
        
        # 2. Перебираем группы
        for group_data in validated_data.get('char_groups', []):
            group = CharacteristicGroup.objects.create(
                category=category,
                name=group_data['name'],
                order=group_data.get('order', 0)
            )
            
            # 3. Готовим шаблоны к массовому созданию (bulk_create)
            templates_to_create = [
                CharacteristicTemplate(
                    group=group,
                    name=t_data['name'],
                    order=t_data.get('order', 0)
                )
                for t_data in group_data.get('templates', [])
            ]
            CharacteristicTemplate.objects.bulk_create(templates_to_create)
            
        return category

    @staticmethod
    def delete_category(category_id: int):
        category = Category.objects.filter(id=category_id).first()
        if not category:
            raise NotFound("Категория не найдена")
        
        # БИЗНЕС-ЛОГИКА: Проверка наличия товаров перед удалением
        if Product.objects.filter(category=category).exists():
            raise ValidationError("Невозможно удалить категорию: в ней еще есть товары.")
        
        category.delete()
