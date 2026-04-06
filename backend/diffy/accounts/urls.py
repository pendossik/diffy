from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ActivateView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uid>/<str:token>/', ActivateView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]