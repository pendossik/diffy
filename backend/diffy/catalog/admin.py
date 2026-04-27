from django.contrib import admin
from catalog.models import (
    Category,
    Product,
    CharacteristicGroup,
    CharacteristicTemplate,
    CharacteristicValue,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ()
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'img_url')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'name')
    list_select_related = ('category',)


@admin.register(CharacteristicGroup)
class CharacteristicGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'order', 'name')
    list_editable = ('order',)


@admin.register(CharacteristicTemplate)
class CharacteristicTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'order')
    list_filter = ('group__category',)
    search_fields = ('name', 'group__name')
    ordering = ('group', 'order', 'name')
    list_editable = ('order',)
    list_select_related = ('group',)


@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'template', 'value')
    list_filter = ('template__group__category', 'product__category')
    search_fields = ('value', 'product__name', 'template__name')
    ordering = ('product', 'template__group__order', 'template__order')
    list_select_related = ('product', 'template__group')