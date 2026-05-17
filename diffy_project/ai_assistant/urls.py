from django.urls import path
from .views.ai_compare import AICompareAPIView

urlpatterns = [
    path('comparison/', AICompareAPIView.as_view(), name='ai-compare'),
]