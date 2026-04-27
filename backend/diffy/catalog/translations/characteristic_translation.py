"""Регистрация моделей characteristic для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions


class CharacteristicGroupTranslationOptions(TranslationOptions):
    fields = ('name',)
    empty_values = None


class CharacteristicTemplateTranslationOptions(TranslationOptions):
    fields = ('name',)
    empty_values = None


class CharacteristicValueTranslationOptions(TranslationOptions):
    fields = ('value',)
    empty_values = None


translator.register('catalog.CharacteristicGroup', CharacteristicGroupTranslationOptions)
translator.register('catalog.CharacteristicTemplate', CharacteristicTemplateTranslationOptions)
translator.register('catalog.CharacteristicValue', CharacteristicValueTranslationOptions)