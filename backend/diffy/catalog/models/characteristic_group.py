from django.db import models


class CharacteristicGroup(models.Model):
    category = models.ForeignKey('catalog.Category', on_delete=models.PROTECT, related_name="char_groups",
                                 verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название группы характеристик")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'catalog'
        ordering = ['order']
        unique_together = ('category', 'name')
        verbose_name = "Группа характеристик"
        verbose_name_plural = "Группы характеристик"

    def __str__(self):
        return f"{self.category.name} - {self.name}"
