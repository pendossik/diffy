from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FavoriteComparisonViewSet, CompareAPIView

router = DefaultRouter()
router.register(r'favorites', FavoriteComparisonViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('comparison/', CompareAPIView.as_view(), name='compare'),
]