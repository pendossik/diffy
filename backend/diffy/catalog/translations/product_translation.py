"""Регистрация модели Product для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions


class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)
    empty_values = None


translator.register('catalog.Product', ProductTranslationOptions)