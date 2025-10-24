from django.urls import path
from .views import register, register_page

urlpatterns = [
    path('register/', register, name='register'),
    path('register-page/', register_page, name='register_page'),
]