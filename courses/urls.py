from django.urls import path
from .views import courses, categories



urlpatterns = [
    path('', courses),
    path('categories/', categories)
]