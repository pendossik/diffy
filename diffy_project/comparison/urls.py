from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.favorite_views import FavoriteComparisonViewSet
from .views.comparison_views import CompareAPIView

router = DefaultRouter()
router.register(r'favorites', FavoriteComparisonViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('comparison/', CompareAPIView.as_view(), name='compare'),
]
