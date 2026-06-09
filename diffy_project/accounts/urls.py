from django.urls import path
from .views.user_views import (
    RegisterAPIView,
    CurrentUserAPIView,
    ActivateAccountAPIView,
    ChangeUsernameAPIView,
    DeleteAccountAPIView,
)
from .views.auth_views import LogoutAPIView
from .views.password_views import (
    ChangePasswordAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    AdminForcePasswordResetAPIView,
)
from .views.admin_views import AdminBlockUserAPIView
from .views.language_views import SetLanguageView

urlpatterns = [
    # Регистрация нового аккаунта
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    # Получение профиля текущего пользователя (кто я?)
    path('current_user/', CurrentUserAPIView.as_view(), name='current_user'),
    
    # Выход (инвалидация refresh токена)
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # Ссылка активации (Backend)
    path('activate/', ActivateAccountAPIView.as_view(), name='activate_account'),

    # Смена username (для авторизованных)
    path('username_change/', ChangeUsernameAPIView.as_view(), name='username_change'),

    path('password_change/', ChangePasswordAPIView.as_view(), name='password_change'),

    # Сброс пароля
    path('password_reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password_reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),

    # Удаление аккаунта
    path('profile_delete/', DeleteAccountAPIView.as_view(), name='delete_account'),

    # Администратору: заблокировать/сменить пароль пользовалеля
    path('admin/users/<int:user_id>/block/', AdminBlockUserAPIView.as_view(), name='admin_block_user'),
    path('admin/users/<int:user_id>/force_password/', AdminForcePasswordResetAPIView.as_view(), name='admin_force_password'),
    
    # Смена языка в куки
    path('set_language/', SetLanguageView.as_view(), name='set_language'),
]
