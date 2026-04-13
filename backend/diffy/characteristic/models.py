from django.db import models
from categories.models import Category
from products.models import Product


class CharacteristicGroup(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="char_groups",
                                 verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название группы характеристик")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('category', 'name')
        verbose_name = "Группа характеристик"
        verbose_name_plural = "Группы характеристик"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class CharacteristicTemplate(models.Model):
    group = models.ForeignKey(
        CharacteristicGroup,
        on_delete=models.CASCADE,
        related_name="templates",
        verbose_name="Группа"
    )
    name = models.CharField(max_length=200, verbose_name="Название характеристики")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        unique_together = ('group', 'name')
        verbose_name = "Характеристика (шаблон)"
        verbose_name_plural = "Характеристики (шаблоны)"

    def __str__(self):
        return f"{self.group.name}: {self.name}"

class CharacteristicValue(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="characteristic_values",
        verbose_name="Товар"
    )
    template = models.ForeignKey(
        CharacteristicTemplate,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name="Характеристика"
    )
    value = models.CharField(max_length=200, verbose_name="Значение")

    def __str__(self):
        return f"{self.product.name}: {self.template.name} = {self.value}"

    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"


