from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Characteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name="Товар")
    name = models.CharField(max_length=100, verbose_name="Наименование характеристики")
    value = models.CharField(max_length=200, verbose_name="Значение")

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"



class FavoritePair(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_pairs")
    product_1 = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorite_as_first")
    product_2 = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorite_as_second")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Избранная пара"
        verbose_name_plural = "Избранные пары"
        unique_together = ("user", "product_1", "product_2")  # защита от дублей

    def save(self, *args, **kwargs):
        # сортируем id чтобы (A,B) == (B,A)
        if self.product_1_id > self.product_2_id:
            self.product_1, self.product_2 = self.product_2, self.product_1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.product_1.name} + {self.product_2.name}"
