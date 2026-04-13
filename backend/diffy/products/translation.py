"""Регистрация модели Product для многоязычности."""
from modeltranslation.translator import translator, TranslationOptions
from .models import Product


class ProductTranslationOptions(TranslationOptions):
    """
    Настройки перевода для модели Product.
    
    Поля, указанные в `fields`, будут дублироваться 
    с суффиксами _ru и _en в базе данных.
    """
    fields = ('name',)
    empty_values = None  # Не заполнять пустые значения автоматически


translator.register(Product, ProductTranslationOptions)