from django.db import models


class CharacteristicTemplate(models.Model):
    group = models.ForeignKey(
        'catalog.CharacteristicGroup',
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
