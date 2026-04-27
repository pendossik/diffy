"""Регистрация модели Category для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions
from categories.models import Category


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    empty_values = None


translator.register(Category, CategoryTranslationOptions)