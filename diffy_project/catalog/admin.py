from django.contrib import admin
import nested_admin
from .models import Category, CharacteristicGroup, CharacteristicTemplate, Product, CharacteristicValue

# 3 уровень (Самый глубокий)
class CharacteristicTemplateInline(nested_admin.NestedTabularInline):
    model = CharacteristicTemplate
    extra = 1
    sortable_field_name = "order" # позволяет перетаскивать элементы мышкой

# 2 уровень
class CharacteristicGroupInline(nested_admin.NestedStackedInline):
    model = CharacteristicGroup
    extra = 1
    inlines = [CharacteristicTemplateInline] # Вкладываем шаблоны в группу
    sortable_field_name = "order"

# 1 уровень (Главная модель)
@admin.register(Category)
class CategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name']
    inlines = [CharacteristicGroupInline] # Вкладываем группы в категорию