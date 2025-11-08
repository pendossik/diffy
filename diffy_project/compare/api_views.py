from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# Список всех категорий для теста
class CategoryListAPIView(generics.ListAPIView):
    """
    generics.ListAPIView — это готовый класс из DRF,
    который автоматически реализует логику для GET-запросов.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Список всех товаров
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    RetrieveAPIView — класс, который обрабатывает GET запросы для одного объекта.
    Он автоматически ищет объект по pk (primary key, то есть id).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
