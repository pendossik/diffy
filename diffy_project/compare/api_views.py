from .models import Category, Product, Characteristic
from .serializers import CategorySerializer, ProductSerializer

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

import re

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import FavoritePair
from .serializers import FavoritePairSerializer, FavoritePairCreateSerializer

# NUMBER_RE = re.compile(r"\d+\.?\d*")

# Список всех категорий для теста
class CategoryListAPIView(generics.ListAPIView):
    """
    generics.ListAPIView — это готовый класс из DRF,
    который автоматически реализует логику для GET-запросов.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Список всех товаров
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    RetrieveAPIView — класс, который обрабатывает GET запросы для одного объекта.
    Он автоматически ищет объект по pk (primary key, то есть id).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# было нужно для сравнения характеристик, сейчас это делается на фронте
# def extract_first_number(s: str):
#     """return float or None"""
#     if not s:
#         return None
#     m = NUMBER_RE.search(s)
#     if not m:
#         return None
#     try:
#         return float(m.group())
#     except ValueError:
#         return None
    

class CompareAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        p1_id = request.data.get("product1")
        p2_id = request.data.get("product2")

        if not p1_id or not p2_id:
            return Response({"detail": "product1 and product2 are required"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if p1_id == p2_id:
            return Response({"detail": "product1 and product2 are the same"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            p1 = Product.objects.select_related("category").prefetch_related("characteristics").get(id=p1_id)
            p2 = Product.objects.select_related("category").prefetch_related("characteristics").get(id=p2_id)
        except Product.DoesNotExist:
            return Response({"detail": "One or both products not found"},
                            status=status.HTTP_404_NOT_FOUND)

        if p1.category_id != p2.category_id:
            return Response({"detail": "Products must be from the same category"},
                            status=status.HTTP_400_BAD_REQUEST)

        def serialize_product(p):
            return {
                "id": p.id,
                "name": p.name,
                "category": {
                    "id": p.category.id,
                    "name": p.category.name
                },
                "characteristics": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "value": c.value
                    }
                    for c in p.characteristics.all()
                ]
            }

        result = {
            "product_1": serialize_product(p1),
            "product_2": serialize_product(p2)
        }

        return Response(result, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_favorite_pair(request):
    serializer = FavoritePairCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    p1 = serializer.validated_data["product_1"]
    p2 = serializer.validated_data["product_2"]

    # сортируем для правильного поиска дублей
    p1, p2 = sorted([p1, p2])

    exists = FavoritePair.objects.filter(
        user=request.user,
        product_1_id=p1,
        product_2_id=p2
    ).exists()

    if exists:
        return Response({"detail": "Уже в избранном."}, status=200)

    FavoritePair.objects.create(
        user=request.user,
        product_1_id=p1,
        product_2_id=p2
    )

    return Response({"detail": "Добавлено в избранное."}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    favorites = FavoritePair.objects.filter(user=request.user).order_by("-created_at")
    serializer = FavoritePairSerializer(favorites, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_favorite(request, pk):
    try:
        fav = FavoritePair.objects.get(id=pk, user=request.user)
    except FavoritePair.DoesNotExist:
        return Response({"detail": "Не найдено."}, status=404)

    fav.delete()
    return Response({"detail": "Удалено."})