from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.get_views import CategoryViewSet, ProductViewSet
from .views.set_views import FastProductCreateView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('createProduct/', FastProductCreateView.as_view(), name='createProduct'),
]