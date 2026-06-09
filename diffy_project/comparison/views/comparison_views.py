from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound

from drf_spectacular.utils import extend_schema

from ..serializers.comparison_serializers import CompareRequestSerializer, CompareResultSerializer
from ..services.comparison_service import ComparisonService


class CompareAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Сравнение товаров (1-3 шт)",
        request=CompareRequestSerializer,
        responses={200: CompareResultSerializer(many=True)},
        tags=['Сравнение']
    )
    def post(self, request):
        serializer = CompareRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            result = ComparisonService.compare_products(serializer.validated_data['product_ids'])
        except NotFound as e:
            return Response({"detail": e.detail}, status=404)

        return Response(result)
