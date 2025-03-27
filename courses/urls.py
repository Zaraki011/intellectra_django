from django.urls import path
from .views import courses, categories
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', courses),
    path('categories/', categories)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)