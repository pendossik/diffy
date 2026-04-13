"""Админ-панель приложения categories с поддержкой переводов."""
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    """
    Админка для модели Category.
    
    Наследуется от TranslationAdmin для отображения полей 
    с суффиксами _ru/_en в одном интерфейсе.
    """
    
    # 🔍 Поля для отображения в списке
    list_display = ('id', 'name', 'name_ru', 'name_en')
    list_display_links = ('id', 'name')
    
    # 🔎 Поля для поиска (ищем по обоим языкам)
    search_fields = ('name_ru', 'name_en')
    
    # 🧭 Фильтры в правой панели
    list_filter = ()  # Пока нет полей для фильтрации, но можно добавить
    
    # ✏️ Поля для редактирования (группировка для удобства)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',),  # name — виртуальное поле, показывает текущий язык
        }),
        ('Переводы', {
            'fields': ('name_ru', 'name_en'),
            'description': 'Заполните названия на обоих языках. '
                          'Если поле пустое, будет использоваться значение из name.'
        }),
    )
    
    # 📋 Настройки формы
    readonly_fields = ()  # Все поля редактируемые
    
    # ⚡ Оптимизация: не нужно, т.к. модель простая
    # list_select_related = ()
    
    # 🗂 Порядок полей в форме (явно указываем для контроля)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Можно добавить кастомную логику, если понадобится
        return form
    
    # 📝 Подсказки для полей (help_text)
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        
        # Добавляем подсказки для полей переводов
        if db_field.name == 'name_ru':
            field.help_text = 'Название категории на русском языке'
        elif db_field.name == 'name_en':
            field.help_text = 'Название категории на английском языке'
        
        return field