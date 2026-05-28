from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.pagination import LimitOffsetPagination

from ..serializers.product_serializers import ProductSerializer, ProductFastCreateSerializer
from ..services.product_service import ProductService

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from ..models import Product


class ProductPagination(LimitOffsetPagination):
    default_limit = 10 # По умолчанию отдавать 10
    max_limit = 20     # Фронтенд не сможет попросить больше 2


@extend_schema_view(
    list=extend_schema(summary="Список всех товаров или выборка по search", tags=['Каталог']),
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

    """
    DRF сначала вызовет ваш get_queryset (отфильтрует по категории),
    а затем сам прогонит результат через SearchFilter

    Пример: GET /products/?category=Смартфоны&search=Iphone
    """
    def get_queryset(self):
        # 1. Получаем базовый queryset
        queryset = super().get_queryset()
        
        # 2. Ищем параметр category в URL (?category=...)
        category_name = self.request.query_params.get('category')
        
        # 3. Если параметр передан, фильтруем базу
        if category_name:
            # Используем iexact для регистронезависимого поиска 
            queryset = queryset.filter(category__name__iexact=category_name)
            
        return queryset


# создание товара
class FastProductCreateView(APIView):
    permission_classes = [IsAdminUser] 

    # Обертка для Swagger (drf-spectacular)
    @extend_schema(
        summary="Быстрое добавление товара через JSON",
        description="Поле value_en НЕ ОБЯЗАТЕЛЬНО! Принимает готовую структуру товара с характеристиками и создает записи в БД.",
        request=ProductFastCreateSerializer,
        responses={
            201: OpenApiResponse(description='{"detail": "Товар успешно добавлен", "product_id": 5}'),
            400: OpenApiResponse(description="Ошибки валидации (неверная категория, структура и т.д.)")
        },
        tags=["Каталог"]
    )
        
    def post(self, request, *args, **kwargs):
        # 1. Проверяем структуру JSON
        serializer = ProductFastCreateSerializer(data=request.data)
        
        # Если структура неверная (нет поля category и т.д.), выбросит 400
        serializer.is_valid(raise_exception=True) 
        
        # 2. Передаем валидные данные в сервис
        # Если бизнес-логика нарушена (категория не найдена), сервис тоже выбросит 400
        product = ProductService.create_product_with_characteristics(serializer.validated_data)
        
        # 3. Возвращаем успешный ответ
        return Response(
            {
                "detail": "Товар успешно добавлен", 
                "product_id": product.id
            }, 
            status=status.HTTP_201_CREATED
        )
    
class ProductDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Удаление товара по ID",
        tags=["Каталог"]
    )
    # удаление товара (с каскадным удалением характеристик)
    def delete(self, request, pk):
        ProductService.delete_product(product_id=pk)
        return Response(
            {"detail": "Товар и его характеристики успешно удалены"}, 
            status=status.HTTP_204_NO_CONTENT
        )
