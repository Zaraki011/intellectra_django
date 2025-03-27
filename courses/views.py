from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Course, Category
from .serializers import CourseSerializer, CategorySerializer

@api_view(['GET'])
def courses(request):
    courses = Course.objects.all()
    data = CourseSerializer(courses, many=True).data
    return Response(data)

@api_view(['GET'])
def categories(request):
    categories = Category.objects.all()
    data = CategorySerializer(categories, many=True).data
    return Response(data)
    


