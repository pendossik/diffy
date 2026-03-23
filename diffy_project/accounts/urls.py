from django.urls import path
# устарели, но пока оставил
from .api_views import RegisterAPIView, CurrentUserAPIView, LogoutAPIView, ActivateAccountAPIView
from .api_views import ChangePasswordAPIView, PasswordResetRequestAPIView, PasswordResetConfirmAPIView
from .api_views import ChangeUsernameAPIView

urlpatterns = [
    # Регистрация нового аккаунта
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    # Получение профиля текущего пользователя (кто я?)
    path('current_user/', CurrentUserAPIView.as_view(), name='current_user'),
    
    # Выход (инвалидация refresh токена)
    path('logout/', LogoutAPIView.as_view(), name='logout'),

        # Ссылка активации (Backend)
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountAPIView.as_view(), name='activate'),

    # Смена username (для авторизованных)
    path('username_change/', ChangeUsernameAPIView.as_view(), name='username_change'),

    path('password_change/', ChangePasswordAPIView.as_view(), name='password_change'),

    # Сброс пароля
    path('password_reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password_reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
]
