"""URL-маршруты приложения catalog."""
from django.urls import path
from catalog.views import (
    CategoryView,
    CategoryDetailView,
    ProductView,
    ProductDetailView,
    CharacteristicGroupView,
    CharacteristicGroupDetailView,
    CharacteristicTemplateView,
    CharacteristicTemplateDetailView,
    CharacteristicValueView,
    CharacteristicValueDetailView,
)

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),

    path('products/', ProductView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('characteristic-groups/', CharacteristicGroupView.as_view(), name='characteristic-group-list'),
    path('characteristic-groups/<int:id>/', CharacteristicGroupDetailView.as_view(), name='characteristic-group-detail'),

    path('characteristic-templates/', CharacteristicTemplateView.as_view(), name='characteristic-template-list'),
    path('characteristic-templates/<int:id>/', CharacteristicTemplateDetailView.as_view(), name='characteristic-template-detail'),

    path('characteristic-values/', CharacteristicValueView.as_view(), name='characteristic-value-list'),
    path('characteristic-values/<int:id>/', CharacteristicValueDetailView.as_view(), name='characteristic-value-detail'),
]