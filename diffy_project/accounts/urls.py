from django.urls import path
# устарели, но пока оставил
from .views import register, register_page, login_user, login_page, current_user, logout_user, profile_page
from .api_views import RegisterAPIView, CurrentUserAPIView, LogoutAPIView#, LoginAPIView

urlpatterns = [
    path('register/', register, name='register'),
    path('register-page/', register_page, name='register_page'),
    # логин устарел, сейчас эта логика в main urls.py как api/token
    path('login/', login_user, name='login'),
    path('login-page/', login_page, name='login_page'),
    path('current_user/', current_user, name='current_user'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile-page/', profile_page, name='profile_page'),
    
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    # был нужен когад использвоали token вместо jwtда
    # path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/current_user/', CurrentUserAPIView.as_view(), name='api_current_user'),

    
]