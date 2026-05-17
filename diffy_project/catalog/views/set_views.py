from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from ..serializers.set_serializers import ProductFastCreateSerializer
from ..services.set_services import create_product_with_characteristics

from drf_spectacular.utils import extend_schema, OpenApiResponse


class FastProductCreateView(APIView):
    permission_classes = [IsAdminUser] 

    # Обертка для Swagger (drf-spectacular)
    @extend_schema(
        summary="Быстрое добавление товара через JSON",
        description="Принимает готовую структуру товара с характеристиками и создает записи в БД.",
        request=ProductFastCreateSerializer,
        responses={
            201: OpenApiResponse(description='{"detail": "Товар успешно добавлен", "product_id": 5}'),
            400: OpenApiResponse(description="Ошибки валидации (неверная категория, структура и т.д.)")
        },
        tags=["Products Admin"]
    )
        
    def post(self, request, *args, **kwargs):
        # 1. Проверяем структуру JSON
        serializer = ProductFastCreateSerializer(data=request.data)
        
        # Если структура неверная (нет поля category и т.д.), выбросит 400
        serializer.is_valid(raise_exception=True) 
        
        # 2. Передаем валидные данные в сервис
        # Если бизнес-логика нарушена (категория не найдена), сервис тоже выбросит 400
        product = create_product_with_characteristics(serializer.validated_data)
        
        # 3. Возвращаем успешный ответ
        return Response(
            {
                "detail": "Товар успешно добавлен", 
                "product_id": product.id
            }, 
            status=status.HTTP_201_CREATED
        )