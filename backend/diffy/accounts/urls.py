from django.urls import path

from accounts.views.auth import RegisterView, ActivateView, LogoutView, LoginView
from accounts.views.profile import ProfileView, CurrentUserView, ChangeUsernameView, DeleteAccountView
from accounts.views.password import ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView
from accounts.views.admin import AdminBlockUserView, AdminForcePasswordResetView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    # Используем JWT, помимо токенов возвращаем информацию о пользователи включая его роль
    path('login/', LoginView.as_view(), name='login'), 

    # Для фронта может быть важно:
    # Было (в ветке Андрея): При успехе возвращает статус 205 Reset Content (без тела ответа).
    # Стало: Возвращает статус 200 OK с телом {"message": "Выход выполнен успешно"}
    path('logout/', LogoutView.as_view(), name='logout'),

    # тут было важно для фронтенда поменять формат ввода токенов 
    # тк react отправляет POST запрос с телом (JSON) а не внутри ссылки
    # Было:
    # path('activate/<str:uid>/<str:token>/', ActivateView.as_view(), name='activate'),
    path('activate/', ActivateView.as_view(), name='activate_account'),


    # тут нужно учесть как было (как сейчас использует фронтенд и как стало)
    # Было: Эндпоинт /current_user/. Отдает:
    #  {"id": 1, "username": "test", "email": "test@test.com"}.

    # Стало: Эндпоинт /profile/. Отдает:
    # {"email": "test@test.com", "role": "user", "is_active": True, "date_joined": "..."}.
    # итог: нужно согласовать с фронтом при запуске
    # пока оставил оба варианта
    path('profile/', ProfileView.as_view(), name='profile'),
    path('current_user/', CurrentUserView.as_view(), name='current_user'),


    path('username_change/', ChangeUsernameView.as_view(), name='username_change'),
    path('profile_delete/', DeleteAccountView.as_view(), name='delete_account'),

    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('admin/users/<int:user_id>/block/', AdminBlockUserView.as_view(), name='admin_block_user'),
    path('admin/users/<int:user_id>/force_password/', AdminForcePasswordResetView.as_view(), name='admin_force_password'),
]