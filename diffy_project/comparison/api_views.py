from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


from .models import FavoriteComparison
from catalog.models import Product
from .serializers import CompareRequestSerializer, CompareResultSerializer, FavoriteComparisonSerializer

# чтобы сваггер понял CompareAPIView
from drf_spectacular.utils import extend_schema


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

        product_ids = serializer.validated_data['product_ids']
        
        # Запрос с оптимизацией
        products = (
            Product.objects.filter(id__in=product_ids)
            .select_related("category")
            .prefetch_related("characteristic_values__template__group")
        )

        if not products.exists():
            return Response({"detail": "Товары не найдены"}, status=404)

        # Сборка данных под ваш формат
        result = []
        for product in products:
            # Группируем характеристики этого товара
            groups_map = {}
            for val in product.characteristic_values.all():
                group_name = val.template.group.name
                if group_name not in groups_map:
                    groups_map[group_name] = []
                
                groups_map[group_name].append({
                    "id": val.id, # или val.template.id
                    "name": val.template.name,
                    "value": val.value
                })

            # Превращаем словарь в список для JSON
            chars_groups = [
                {"name": g_name, "characteristics": chars} 
                for g_name, chars in groups_map.items()
            ]

            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category.name,
                "img": product.img,
                "characteristics_groups": chars_groups
            })

        # Валидируем финальным сериализатором (чтобы быть уверенным в формате)
        return Response(result)


class FavoriteComparisonViewSet(viewsets.ModelViewSet):
    # Теперь это называется FavoriteComparison
    queryset = FavoriteComparison.objects.all()
    serializer_class = FavoriteComparisonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит и может удалять только свои карточки
        return FavoriteComparison.objects.filter(user=self.request.user).prefetch_related('products')

    @extend_schema(summary="Список избранных сравнений", tags=['Избранное'])
    def list(self, request, *args, **kwargs): return super().list(request, *args, **kwargs)

    @extend_schema(summary="Добавить сравнение в избранное", tags=['Избранное'])
    def create(self, request, *args, **kwargs): return super().create(request, *args, **kwargs)

    @extend_schema(summary="Удалить карточку из избранного", tags=['Избранное'])
    def destroy(self, request, *args, **kwargs): return super().destroy(request, *args, **kwargs)