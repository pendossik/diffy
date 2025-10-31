from django.urls import path
from .views import register, register_page, login_user, login_page

urlpatterns = [
    path('register/', register, name='register'),
    path('register-page/', register_page, name='register_page'),
    path('login/', login_user, name='login'),
    path('login-page/', login_page, name='login_page'),
]