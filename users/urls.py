from django.urls import path
from .views import register, login, users, user, MeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', users, name='user-list'),
    path('<str:pk>/', user, name='user-detail'),
    path('me/', MeView.as_view(), name='me'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
