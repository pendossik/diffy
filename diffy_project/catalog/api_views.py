from rest_framework import viewsets
from rest_framework.permissions import AllowAny


from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# чтобы сваггер понял CompareAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(summary="Список категорий", tags=['Каталог']),
    retrieve=extend_schema(summary="Детали категории", tags=['Каталог']),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Автоматически создает:
    GET /categories/
    GET /categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

@extend_schema_view(
    list=extend_schema(summary="Список всех товаров", tags=['Каталог']),
    retrieve=extend_schema(summary="Детали товара", tags=['Каталог']),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Автоматически создает:
    GET /products/
    GET /products/{id}/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]