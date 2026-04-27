"""Регистрация модели Category для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    empty_values = None


translator.register('catalog.Category', CategoryTranslationOptions)