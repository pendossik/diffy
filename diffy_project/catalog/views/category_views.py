from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser

from ..models import Category
from ..serializers.category_serializers import CategorySerializer, CategoryCreateSerializer
from ..services.category_service import CategoryService

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample


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


class CategoryManageAPIView(APIView):
    # доступ только для is_staff=True
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Создание категории с каркасом характеристик",
        description="Создает категорию, группы характеристик и сами характеристики за один запрос",
        request=CategoryCreateSerializer,
        examples=[
            OpenApiExample(
                name="Шаблон (Смартфоны)",
                description="Пример вложенной структуры для создания категории",
                value={
                    "name": "Смартфоны",
                    "char_groups": [
                        {
                            "name": "Экран",
                            "order": 1,
                            "templates": [
                                {"name": "Диагональ", "order": 1},
                                {"name": "Разрешение", "order": 2},
                                {"name": "Тип матрицы", "order": 3}
                            ]
                        },
                        {
                            "name": "Процессор",
                            "order": 2,
                            "templates": [
                                {"name": "Модель", "order": 1},
                                {"name": "Ядра", "order": 2}
                            ]
                        }
                    ]
                },
                request_only=True, # Показывать этот пример только для тела запроса
            )
        ],
        tags=["Каталог"]
    )
    # создание категории
    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # передаем валидные данные в сервис
        category = CategoryService.create_category_with_hierarchy(serializer.validated_data)
        
        return Response(
            {"detail": "Категория и структура характеристик успешно созданы", "category_id": category.id},
            status=status.HTTP_201_CREATED
        )
    

class CategoryDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Удаление категории по ID",
        description="Можно удалить только если нет товаров этой категории",
        tags=["Каталог"]
    )
    # удаление категории
    def delete(self, request, pk):
        CategoryService.delete_category(category_id=pk)
        return Response(
            {"detail": "Категория успешно удалена"}, 
            status=status.HTTP_204_NO_CONTENT
        )
