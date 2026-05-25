from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.product_views import ProductViewSet, FastProductCreateView, ProductDeleteAPIView
from .views.category_views import  CategoryViewSet, CategoryManageAPIView, CategoryDeleteAPIView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('createProduct/', FastProductCreateView.as_view(), name='createProduct'),

    # POST для создания категории с каркасом
    path('admin/categories/', CategoryManageAPIView.as_view(), name='admin-category-create'),
    
    # DELETE для удаления категории (передаем ID категории)
    path('admin/categories/<int:pk>/', CategoryDeleteAPIView.as_view(), name='admin-category-delete'),
    
    # DELETE для удаления товара (передаем ID товара)
    path('admin/products/<int:pk>/', ProductDeleteAPIView.as_view(), name='admin-product-delete'),
]