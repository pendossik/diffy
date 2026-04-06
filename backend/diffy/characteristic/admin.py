"""Админка приложения characteristic."""
from django.contrib import admin
from .models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


@admin.register(CharacteristicGroup)
class CharacteristicGroupAdmin(admin.ModelAdmin):
    """Админка для групп характеристик."""
    list_display = ('id', 'category', 'name', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'order')
    list_editable = ('order',)


@admin.register(CharacteristicTemplate)
class CharacteristicTemplateAdmin(admin.ModelAdmin):
    """Админка для шаблонов характеристик."""
    list_display = ('id', 'group', 'name', 'order')
    list_filter = ('group', 'group__category')
    search_fields = ('name', 'group__name')
    ordering = ('group', 'order')
    list_editable = ('order',)


@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(admin.ModelAdmin):
    """Админка для значений характеристик."""
    list_display = ('id', 'product', 'template', 'value')
    list_filter = ('template__group', 'product__category')
    search_fields = ('product__name', 'template__name', 'value')
    ordering = ('product', 'template__group', 'template')
