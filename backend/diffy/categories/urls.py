from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView

urlpatterns = [
    # GET (список с поиском) / POST (создание)
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    # GET (детали) / PUT (обновление) / PATCH (частичное) / DELETE (удаление)
    path('<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]