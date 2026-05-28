from modeltranslation.translator import register, TranslationOptions
from .models import Category, CharacteristicGroup, CharacteristicTemplate, Product, CharacteristicValue

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CharacteristicGroup)
class CharacteristicGroupTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CharacteristicTemplate)
class CharacteristicTemplateTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CharacteristicValue)
class CharacteristicValueTranslationOptions(TranslationOptions):
    fields = ('value',)