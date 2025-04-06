from django.urls import path
from .views import courses, categories, course, quizzes, submit_quiz, add_course



urlpatterns = [
    path('', courses),
    path('categories/', categories),
    path('<str:pk>/', course, name='course-detail'),
    path('<str:pk>/quizzes/', quizzes, name='quizzes'),
    path('api/submit-quiz/', submit_quiz),
    path('api/add-course/', add_course),
]