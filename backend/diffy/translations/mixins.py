from django.db import models
from django.contrib.contenttypes.models import ContentType
from .models import Translation


class TranslatableMixin(models.Model):
    """
    Миксин для добавления поддержки переводов в любую модель.
    Добавляет поле name (fallback на русском) и методы для работы с переводами.
    """

    # Основное поле (fallback, обычно русское)
    name = models.CharField(
        max_length=200,
        verbose_name="Название (по умолчанию)"
    )

    class Meta:
        abstract = True

    def get_translation(self, field_name, lang='ru'):
        """
        Получить перевод для конкретного поля.
        Если перевода нет — вернёт основное значение из модели.
        """
        content_type = ContentType.objects.get_for_model(self.__class__)

        translation = Translation.objects.filter(
            content_type=content_type,
            object_id=self.id,
            language=lang,
            field_name=field_name
        ).first()

        return translation.value if translation else getattr(self, field_name, '')

    def set_translation(self, field_name, lang, value):
        """
        Установить перевод для поля.
        Создаёт или обновляет запись в таблице Translation.
        """
        content_type = ContentType.objects.get_for_model(self.__class__)

        Translation.objects.update_or_create(
            content_type=content_type,
            object_id=self.id,
            language=lang,
            field_name=field_name,
            defaults={'value': value}
        )

    def get_translated_name(self, lang='ru'):
        """Получить переведённое название"""
        return self.get_translation('name', lang)

    def get_all_translations(self, field_name='name'):
        """
        Получить все доступные переводы для поля.
        Возвращает dict: {'ru': '...', 'en': '...', ...}
        """
        content_type = ContentType.objects.get_for_model(self.__class__)

        translations = Translation.objects.filter(
            content_type=content_type,
            object_id=self.id,
            field_name=field_name
        )

        result = {lang: getattr(self, field_name) for lang in ['ru', 'en', 'zh', 'es', 'de']}

        for t in translations:
            result[t.language] = t.value

        return result