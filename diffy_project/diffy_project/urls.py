"""
URL configuration for diffy_project project.

"""
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views.auth_views import EmailTokenObtainPairView

# Импорты для Swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    
    # JWT
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # РЕФАКТОРИНГ: разделили старый compare на два приложения
    # path('api/compare/', include('compare.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/comparison/', include('comparison.urls')),

    path('api/ai/', include('ai_assistant.urls')),

    # --- SWAGGER И СХЕМА ---
    # 1. Ссылка на скачивание схемы (YAML файл)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. Сам интерфейс Swagger UI (то, что нужно фронтендерам)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. Альтернативный интерфейс Redoc (по желанию, выглядит чище)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
