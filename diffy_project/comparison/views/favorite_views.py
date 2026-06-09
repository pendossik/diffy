from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from ..models import FavoriteComparison
from ..serializers.favorite_serializers import FavoriteComparisonSerializer
from ..services.favorite_service import FavoriteComparisonService


class FavoriteComparisonViewSet(viewsets.ModelViewSet):
    queryset = FavoriteComparison.objects.all()
    serializer_class = FavoriteComparisonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteComparisonService.get_queryset_for_user(self.request.user)

    @extend_schema(summary="Список избранных сравнений", tags=['Избранное'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Добавить сравнение в избранное", tags=['Избранное'])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comparison = FavoriteComparisonService.create_favorite(
            request.user,
            serializer.validated_data['product_ids'],
        )
        output_serializer = self.get_serializer(comparison)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(summary="Удалить карточку из избранного", tags=['Избранное'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
