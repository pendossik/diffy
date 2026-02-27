from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Translation(models.Model):
    """
    Универсальная таблица переводов для ЛЮБОЙ модели.
    Хранит переводы полей в формате: модель + объект + язык + поле + значение
    """

    # Generic relation к любой модели
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Тип контента"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID объекта")
    content_object = GenericForeignKey('content_type', 'object_id')

    # Данные перевода
    language = models.CharField(
        max_length=2,
        choices=[
            ('ru', 'Русский'),
            ('en', 'English'),
            ('zh', 'Chinese'),
            ('es', 'Spanish'),
            ('de', 'German'),
        ],
        verbose_name="Язык"
    )
    field_name = models.CharField(
        max_length=50,
        verbose_name="Имя поля"
    )
    value = models.TextField(
        verbose_name="Значение перевода"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'translations_translation'
        verbose_name = "Перевод"
        verbose_name_plural = "Переводы"
        unique_together = ('content_type', 'object_id', 'language', 'field_name')
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'language']),
            models.Index(fields=['language', 'field_name']),
        ]
        ordering = ['language', 'field_name']

    def __str__(self):
        return f"{self.content_object} [{self.language}] {self.field_name}"