from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from .models import Course, Category, Quiz, Question, Choice, QuizResult
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .serializers import CourseSerializer, CategorySerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_course(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(professor=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def courses(request):
    courses = Course.objects.all()
    data = CourseSerializer(courses, many=True, context={'request': request}).data
    return Response(data)

@api_view(['GET'])
def course(request, pk):
    course = Course.objects.get(id = pk)
    data = CourseSerializer(course , many=False, context={'request': request}).data
    return Response(data)

@api_view(['GET'])
def categories(request):
    categories = Category.objects.all()
    data = CategorySerializer(categories, many=True, context={'request': request}).data
    return Response(data)
    
@api_view(['GET'])
def quizzes(request, course_id):
    quizzes = Quiz.objects.filter(course_id=course_id)
    data = QuizSerializer(quizzes, many=True).data
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request):
    user = request.user
    quiz_id = request.data.get('quiz_id')
    answers = request.data.get('answers')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    total_questions = quiz.questions.count()
    correct_answers = 0

    for answer in answers:
        question = get_object_or_404(Question, id=answer['question_id'], quiz=quiz)
        selected_choice = get_object_or_404(Choice, id=answer['selected_choice_id'], question=question)
        if selected_choice.is_correct:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100

    # Save the result
    QuizResult.objects.create(
        student=user,
        quiz=quiz,
        score=score
    )

    return Response({
        'message': 'Quiz submitted successfully',
        'score': score
    })