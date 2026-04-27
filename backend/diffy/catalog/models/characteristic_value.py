from django.db import models


class CharacteristicValue(models.Model):
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name="characteristic_values",
        verbose_name="Товар"
    )
    template = models.ForeignKey(
        'catalog.CharacteristicTemplate',
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
