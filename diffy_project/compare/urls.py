from django.urls import path
from .api_views import CategoryListAPIView, ProductListAPIView, ProductDetailAPIView, CompareAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='api_categories'),
    path('products/', ProductListAPIView.as_view(), name='api_products'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('comparetest/', CompareAPIView.as_view(), name='compare-test')
]
