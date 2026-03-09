from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination


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



class ProductPagination(LimitOffsetPagination):
    default_limit = 10 # По умолчанию отдавать 10
    max_limit = 20     # Фронтенд не сможет попросить больше 2


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

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    # если заменить ['^name'] то поиск будет быстрее, но только с начала слова, а не по всей строке

    pagination_class = ProductPagination # Подключаем пагинацию для лимита 10