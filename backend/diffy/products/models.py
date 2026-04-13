from django.db import models
from categories.models import Category


class Product(models.Model):
    """
    Модель товара.
    
    Поддерживает многоязычность через django-modeltranslation.
    Изображения хранятся в media/products/.
    """
    name = models.CharField(max_length=200, verbose_name="Наименование")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория",
        related_name='products'
    )
    img = models.CharField(
        max_length=300, 
        verbose_name="Фото", 
        null=True, 
        blank=True,
        help_text="Путь к изображению относительно MEDIA_URL"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['category', 'name']