from django.db import models
from accounts.models import User
from catalog.models import Product

class FavoriteComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_comparisons")
    products = models.ManyToManyField(Product, related_name="favorited_in_sets")
    created_at = models.DateTimeField(auto_now_add=True)

    # Хэш для быстрой проверки на дубликаты
    # Позволит быстро понять, что набор [1,2] и [2,1] — это одно и то же
    products_hash = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'comparisons'
        verbose_name = "Избранное сравнение"
        verbose_name_plural = "Избранные сравнения"
        ordering = ['-created_at']
        unique_together = ('user', 'products_hash')

    def __str__(self):
        return f"{self.user.username}'s set ({self.products.count()} items)"