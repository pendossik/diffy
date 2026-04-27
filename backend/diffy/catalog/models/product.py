from django.db import models
from catalog.models.category import Category


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория",
        related_name='products'
    )
    img_url = models.CharField(
        max_length=300, 
        verbose_name="Фото", 
        null=True, 
        blank=True,
        help_text="Путь к изображению в сети"
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'catalog'
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['category', 'name']