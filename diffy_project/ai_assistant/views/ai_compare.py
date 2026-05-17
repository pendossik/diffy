# import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers.ai_compare import AICompareRequestSerializer, AICompareResponseSerializer
from ..services.ai_service import generate_comparison_summary

class AICompareAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="ИИ: Сравнение товаров",
        description="Генерирует умное сравнение на основе характеристик выбранных устройств.",
        tags=['AI Assistant'],
        request=AICompareRequestSerializer,
        responses={200: AICompareResponseSerializer},
        examples=[
            OpenApiExample(
                "Пример запроса (2 товара)",
                summary="Сравнить 2 товара",
                description="Подставь сюда реальные ID из твоей БД",
                value={"product_ids": [6, 8]}, # iPhone Air | Google Pixel 9 Pro
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = AICompareRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        product_ids = serializer.validated_data['product_ids']
        
        # Запрос в сервис
        summary_text = generate_comparison_summary(product_ids)

        return Response({"summary": summary_text})