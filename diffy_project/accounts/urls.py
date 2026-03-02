from django.urls import path
# устарели, но пока оставил
from .views import register, register_page, login_user, login_page, current_user, logout_user, profile_page
from .api_views import RegisterAPIView, CurrentUserAPIView, LogoutAPIView, ActivateAccountAPIView#, LoginAPIView

urlpatterns = [
    # Регистрация нового аккаунта
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    # Получение профиля текущего пользователя (кто я?)
    path('current_user/', CurrentUserAPIView.as_view(), name='current_user'),
    
    # Выход (инвалидация refresh токена)
    path('logout/', LogoutAPIView.as_view(), name='logout'),

        # Ссылка активации (Backend)
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountAPIView.as_view(), name='activate'),
]
