from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, FavoritePairViewSet, CompareAPIView

# Роутер сам создаст нужные URL
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'favorites', FavoritePairViewSet, basename='favoritepair')

urlpatterns = [
    path('', include(router.urls)),
    path('comparetest/', CompareAPIView.as_view(), name='comparetest'),
    # было без router
    # path('categories/', CategoryListAPIView.as_view(), name='api_categories'),
    # path('products/', ProductListAPIView.as_view(), name='api_products'),
    # path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    # path('comparetest/', CompareAPIView.as_view(), name='compare-test'),
    # path("favorites/add/", add_favorite_pair),
    # path("favorites/", list_favorites),
    # path("favorites/<int:pk>/", delete_favorite),
]
