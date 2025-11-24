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

NUMBER_RE = re.compile(r"\d+\.?\d*")

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


def extract_first_number(s: str):
    """return float or None"""
    if not s:
        return None
    m = NUMBER_RE.search(s)
    if not m:
        return None
    try:
        return float(m.group())
    except ValueError:
        return None
    
class CompareAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST body: { "product1": <id>, "product2": <id> }
        """
        p1_id = request.data.get("product1")
        p2_id = request.data.get("product2")

        if p1_id is None or p2_id is None:
            return Response({"detail": "product1 and product2 ids are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            p1 = Product.objects.select_related('category').get(pk=p1_id)
            p2 = Product.objects.select_related('category').get(pk=p2_id)
        except Product.DoesNotExist:
            return Response({"detail": "One or both products not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if p1.category_id != p2.category_id:
            return Response({"detail": "Products must be from the same category."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Собираем все имена характеристик для данной категории
        char_names_qs = Characteristic.objects.filter(
            product__category=p1.category
        ).values_list('name', flat=True).distinct()
        char_names = list(char_names_qs)

        # Для each name получаем значение для каждого продукта (или "-")
        # Можно оптимизировать: взять характеристики только для двух продуктов, сгруппировать по имени.
        # Тут простая реализация:
        p1_chars = {c.name: c.value for c in Characteristic.objects.filter(product=p1)}
        p2_chars = {c.name: c.value for c in Characteristic.objects.filter(product=p2)}

        characteristics = []

        for name in char_names:
            v1 = p1_chars.get(name, "-")
            v2 = p2_chars.get(name, "-")

            # если у одного "-" — "-" считается хуже
            if v1 == "-" and v2 != "-":
                comparison = "worse"
            elif v2 == "-" and v1 != "-":
                comparison = "better"
            else:
                # оба имеют значения (возможно оба "-") или оба имеют строки
                num1 = extract_first_number(v1) if v1 != "-" else None
                num2 = extract_first_number(v2) if v2 != "-" else None

                if num1 is not None and num2 is not None:
                    # сравниваем по числам
                    if num1 > num2:
                        comparison = "better"
                    elif num1 < num2:
                        comparison = "worse"
                    else:
                        comparison = "equal"
                elif num1 is not None and num2 is None:
                    # у первого есть число, у второго нет -> считаем число лучше
                    comparison = "better"
                elif num1 is None and num2 is not None:
                    comparison = "worse"
                else:
                    # нет чисел у обоих -> текстовые сравниваем как equal
                    comparison = "equal"

            characteristics.append({
                "name": name,
                "product1": v1,
                "product2": v2,
                "comparison": comparison
            })

        result = {
            "product1": {"id": p1.id, "name": p1.name},
            "product2": {"id": p2.id, "name": p2.name},
            "category": {"id": p1.category.id, "name": p1.category.name},
            "characteristics": characteristics
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

    # проверяем дубликаты
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