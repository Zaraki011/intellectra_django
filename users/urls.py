from django.urls import path
from .views import register, login, users
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('users/', users, name='user-list'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
