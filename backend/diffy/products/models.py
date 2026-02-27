from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")

    img = models.CharField(max_length=300, verbose_name="Фото", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"