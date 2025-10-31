from django.urls import path
from .views import register, register_page, login_user, login_page, current_user, logout_user, profile_page

urlpatterns = [
    path('register/', register, name='register'),
    path('register-page/', register_page, name='register_page'),
    path('login/', login_user, name='login'),
    path('login-page/', login_page, name='login_page'),
    path('current_user/', current_user, name='current_user'),
    path('logout/', logout_user, name='logout_user'),
    path('profile-page/', profile_page, name='profile_page'),
]