from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from .models import Category, Product, FavoritePair
from .serializers import CategorySerializer, ProductSerializer, FavoritePairSerializer, CompareRequestSerializer, CompareResultSerializer

# чтобы сваггер понял CompareAPIView
from drf_spectacular.utils import extend_schema, inline_serializer, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers


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

@extend_schema_view(
    list=extend_schema(summary="Список избранных пар", tags=['Избранное']),
    create=extend_schema(summary="Добавить пару в избранное", tags=['Избранное']),
    destroy=extend_schema(summary="Удалить из избранного", tags=['Избранное']),
)
class FavoritePairViewSet(viewsets.ModelViewSet):
    """
    Автоматически создает:
    GET /favorites/ (список)
    POST /favorites/ (добавить)
    DELETE /favorites/{id}/ (удалить)
    """
    # Добавляем эту строку для Сваггера (чтобы он определил тип id):
    queryset = FavoritePair.objects.all() 

    serializer_class = FavoritePairSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только пары текущего пользователя
        return FavoritePair.objects.filter(user=self.request.user).order_by("-created_at")


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
    # def post(self, request):
    #     # 1. Валидация входных данных через сериализатор
    #     request_serializer = CompareRequestSerializer(data=request.data)
    #     if not request_serializer.is_valid():
    #         return Response(request_serializer.errors, status=400)

    #     product_ids = request_serializer.validated_data['product_ids']

    #     if not (1 <= len(product_ids) <= 3):
    #         return Response({"detail": "Выберите от 1 до 3 товаров"}, status=400)

    #     products = (
    #         Product.objects.filter(id__in=product_ids)
    #         .select_related("category")
    #         .prefetch_related(
    #             "characteristic_values__template__group"
    #         )
    #     )

    #     # Важно: QuerySet ленивый. Чтобы prefetch сработал эффективно, 
    #     # лучше превратить его в список, если вы собираетесь его сортировать
    #     products_list = list(products)

    #     if not products_list:
    #         return Response({"detail": "Товары не найдены"}, status=404)

    #     # Проверка на одну категорию (как и раньше)
    #     first_category = products_list[0].category_id
    #     if not all(p.category_id == first_category for p in products_list):
    #         return Response({"detail": "Товары должны быть из одной категории"}, status=400)

    #     serializer = ProductSerializer(products_list, many=True)
    #     return Response(serializer.data)

# class CompareAPIView(APIView):
#     permission_classes = [AllowAny]

    # @extend_schema(
    #     summary="Сравнение товаров (1-3 шт)",
    #     description="Принимает список ID товаров одной категории. Возвращает их детали и характеристики.",
    #     request=CompareRequestSerializer,
    #     responses={
    #         200: ProductSerializer(many=True),
    #         400: inline_serializer(
    #             name='ErrorResponse',
    #             fields={'detail': serializers.CharField()}
    #         )
    #     },
    #     tags=['Сравнение']
    # )

#     def post(self, request):
#         p1_id = request.data.get("product1")
#         p2_id = request.data.get("product2")

#         if not p1_id or not p2_id:
#             return Response({"detail": "product1 and product2 IDs are required"}, status=400)
        
#         # Оптимизированный запрос к БД
#         # prefetch_related подтягивает сразу все группы и характеристики в них
#         # TODO: Optimize N+1 query (В ProductSerializer метод get_characteristics_groups и внутри CharacteristicGroupSerializer get_characteristics(self, group))
#         products = Product.objects.filter(id__in=[p1_id, p2_id]) \
#                                   .select_related("category") \
#                                   .prefetch_related("category__char_groups__templates__values")

#         if len(products) != 2:
#             return Response({"detail": "One or both products not found"}, status=404)

#         p1, p2 = products[0], products[1]

#         if p1.category_id != p2.category_id:
#             return Response({"detail": "Products must be from the same category"}, status=400)
        
#         serializer = ProductSerializer([p1, p2], many=True)
#         return Response(serializer.data, status=200)
