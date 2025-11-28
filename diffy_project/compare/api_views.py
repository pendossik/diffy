from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from .models import Category, Product, FavoritePair
from .serializers import CategorySerializer, ProductSerializer, FavoritePairSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Автоматически создает:
    GET /categories/
    GET /categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Автоматически создает:
    GET /products/
    GET /products/{id}/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class FavoritePairViewSet(viewsets.ModelViewSet):
    """
    Автоматически создает:
    GET /favorites/ (список)
    POST /favorites/ (добавить)
    DELETE /favorites/{id}/ (удалить)
    """
    serializer_class = FavoritePairSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только пары текущего пользователя
        return FavoritePair.objects.filter(user=self.request.user).order_by("-created_at")
    

class CompareAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        p1_id = request.data.get("product1")
        p2_id = request.data.get("product2")

        if not p1_id or not p2_id:
            return Response({"detail": "product1 and product2 IDs are required"}, status=400)
        
        # Оптимизированный запрос к БД (в один заход, если повезет, или два быстрых)
        products = Product.objects.filter(id__in=[p1_id, p2_id])\
                                  .select_related("category")\
                                  .prefetch_related("characteristics")

        if len(products) != 2:
             return Response({"detail": "One or both products not found"}, status=404)

        p1, p2 = products[0], products[1]

        if p1.category_id != p2.category_id:
             return Response({"detail": "Products must be from the same category"}, status=400)
        
        serializer = ProductSerializer([p1, p2], many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def add_favorite_pair(request):
#     serializer = FavoritePairCreateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)

#     p1 = serializer.validated_data["product_1"]
#     p2 = serializer.validated_data["product_2"]

#     # сортируем для правильного поиска дублей
#     p1, p2 = sorted([p1, p2])

#     exists = FavoritePair.objects.filter(
#         user=request.user,
#         product_1_id=p1,
#         product_2_id=p2
#     ).exists()

#     if exists:
#         return Response({"detail": "Уже в избранном."}, status=200)

#     FavoritePair.objects.create(
#         user=request.user,
#         product_1_id=p1,
#         product_2_id=p2
#     )

#     return Response({"detail": "Добавлено в избранное."}, status=status.HTTP_201_CREATED)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def list_favorites(request):
#     favorites = FavoritePair.objects.filter(user=request.user).order_by("-created_at")
#     serializer = FavoritePairSerializer(favorites, many=True)
#     return Response(serializer.data)


# @api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
# def delete_favorite(request, pk):
#     try:
#         fav = FavoritePair.objects.get(id=pk, user=request.user)
#     except FavoritePair.DoesNotExist:
#         return Response({"detail": "Не найдено."}, status=404)

#     fav.delete()
#     return Response({"detail": "Удалено."})