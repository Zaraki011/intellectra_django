from django.urls import path
from .views import courses, categories, course, quizzes, submit_quiz, add_course, EnrollCourseView, CreateReviewView, CourseReviewsView, MyEnrolledCoursesView



urlpatterns = [
    path('', courses),
    path('categories/', categories),
    path('api/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('<str:pk>/', course, name='course-detail'),
    path('<str:pk>/quizzes/', quizzes, name='quizzes'),
    path('api/submit-quiz/', submit_quiz),
    path('api/add-course/', add_course),
    path('api/enroll/my-courses/', MyEnrolledCoursesView.as_view(), name='my-courses'),
    path('api/reviews/add/', CreateReviewView.as_view(), name='add-review'),
    path('api/reviews/<int:cours_id>/', CourseReviewsView.as_view(), name='course-reviews'),
]