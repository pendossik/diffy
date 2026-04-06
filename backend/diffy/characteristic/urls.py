from django.urls import path
from .views import (
    CategoryCharacteristicsGroupsView,
    
    CharacteristicGroupListCreateView,
    CharacteristicGroupDetailView,
    
    CharacteristicTemplateListCreateView,
    CharacteristicTemplateDetailView,
    
    ProductCharacteristicListCreateView,
    ProductCharacteristicDetailView,
)

urlpatterns = [
    # Публичный список групп для категории
    path('categories/<int:id>/characteristics-groups/', 
         CategoryCharacteristicsGroupsView.as_view(), 
         name='category-characteristics-groups'),

    # Группы характеристик
    path('characteristic/groups/', 
         CharacteristicGroupListCreateView.as_view(), 
         name='characteristic-groups-list'),
    path('characteristic/groups/<int:pk>/', 
         CharacteristicGroupDetailView.as_view(), 
         name='characteristic-group-detail'),

    # Шаблоны характеристик
    path('characteristic/templates/', 
         CharacteristicTemplateListCreateView.as_view(), 
         name='characteristic-templates-list'),
    path('characteristic/templates/<int:pk>/', 
         CharacteristicTemplateDetailView.as_view(), 
         name='characteristic-template-detail'),

    # Значения характеристик товара
    path('products/<int:id>/characteristics/', 
         ProductCharacteristicListCreateView.as_view(), 
         name='product-characteristics-list'),
    path('products/<int:id>/characteristics/<int:pk>/', 
         ProductCharacteristicDetailView.as_view(), 
         name='product-characteristic-detail'),
]