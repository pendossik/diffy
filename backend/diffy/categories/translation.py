"""Регистрация модели Category для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions
from .models import Category


class CategoryTranslationOptions(TranslationOptions):
    """
    Настройки перевода для модели Category.
    
    Поля, указанные в `fields`, будут дублироваться 
    с суффиксами _ru и _en в базе данных.
    """
    fields = ('name',)
    empty_values = None  # Не заполнять пустые значения автоматически


translator.register(Category, CategoryTranslationOptions)