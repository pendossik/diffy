from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, FavoritePairViewSet, CompareAPIView

# Роутер сам создаст нужные URL
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'favorites', FavoritePairViewSet, basename='favoritepair')

urlpatterns = [
    # Все стандартные пути: 
    # /compare/categories/
    # /compare/products/
    # /compare/favorites/
    path('', include(router.urls)),

    # Специальный эндпоинт для сравнения 1-3 товаров
    path('comparetest/', CompareAPIView.as_view(), name='comparetest'),
]
