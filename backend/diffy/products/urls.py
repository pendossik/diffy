from django.urls import path
from .views import ProductListCreateView, ProductDetailView

urlpatterns = [
    # GET (список с поиском и фильтрацией) / POST (создание)
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    # GET (детали) / PUT (обновление) / PATCH (частичное) / DELETE (удаление)
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]