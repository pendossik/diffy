from django.urls import path
from .views import (
    FavoriteComparisonListCreateView,
    FavoriteComparisonDetailView,
    ComparisonCharacteristicsView,
)

urlpatterns = [
    # GET (список избранных) / POST (добавить в избранное)
    path('favorites/', FavoriteComparisonListCreateView.as_view(), name='favorite-comparisons-list-create'),
    # GET (детали) / DELETE (удалить из избранного)
    path('favorites/<int:id>/', FavoriteComparisonDetailView.as_view(), name='favorite-comparison-detail'),
    # GET /api/comparisons/characteristics/?product_ids=1,2,3
    path('characteristics/', ComparisonCharacteristicsView.as_view(), name='comparison-characteristics'),
]
