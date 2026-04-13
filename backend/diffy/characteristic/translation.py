"""Регистрация моделей characteristic для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions
from .models import CharacteristicGroup, CharacteristicTemplate, CharacteristicValue


class CharacteristicGroupTranslationOptions(TranslationOptions):
    """
    Настройки перевода для модели CharacteristicGroup.

    Поля, указанные в `fields`, будут дублироваться
    с суффиксами _ru и _en в базе данных.
    """
    fields = ('name',)
    empty_values = None


class CharacteristicTemplateTranslationOptions(TranslationOptions):
    """
    Настройки перевода для модели CharacteristicTemplate.
    """
    fields = ('name',)
    empty_values = None


class CharacteristicValueTranslationOptions(TranslationOptions):
    """
    Настройки перевода для модели CharacteristicValue.
    """
    fields = ('value',)
    empty_values = None


translator.register(CharacteristicGroup, CharacteristicGroupTranslationOptions)
translator.register(CharacteristicTemplate, CharacteristicTemplateTranslationOptions)
translator.register(CharacteristicValue, CharacteristicValueTranslationOptions)
