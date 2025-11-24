from django.urls import path
from .api_views import CategoryListAPIView, ProductListAPIView, ProductDetailAPIView, CompareAPIView, add_favorite_pair, list_favorites, delete_favorite

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='api_categories'),
    path('products/', ProductListAPIView.as_view(), name='api_products'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('comparetest/', CompareAPIView.as_view(), name='compare-test'),
    path("favorites/add/", add_favorite_pair),
    path("favorites/", list_favorites),
    path("favorites/<int:pk>/", delete_favorite),
]
