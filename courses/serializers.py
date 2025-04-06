from rest_framework import serializers
from .models import Course, Category, CourseSection, CoursePdfInternal, Quiz, Question, Choice, QuizResult

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'course', 'questions']


class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = ['id', 'title', 'content', 'order']  # Adjust fields as necessary

class CoursePdfInternalSerializer(serializers.ModelSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)

    class Meta:
        model = CoursePdfInternal
        fields = ['id', 'name', 'table_of_contents', 'sections']
        read_only_fields = ['name', 'table_of_contents', 'sections']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    professor = serializers.CharField(source='professor.get_full_name', read_only=True)
    category = serializers.CharField(source='category.categoryName', read_only=True)
    pdf_internal_data = CoursePdfInternalSerializer(read_only=True)
    # file = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    

    # def get_file(self, obj):
    #     if obj.file:  
    #         request = self.context.get('request', None)  # Vérifie si request est présent
    #         if request is not None:  
    #             return request.build_absolute_uri(obj.file.url)  # Génère une URL complète
    #         return f"{settings.MEDIA_URL}{obj.file}"  # Fallback si request est None
    #     return None  # Retourne `None` si l'avatar est vide

    def get_image(self, obj):
        if obj.image:  
            request = self.context.get('request', None)  # Vérifie si request est présent
            if request is not None:  
                return request.build_absolute_uri(obj.image.url)  # Génère une URL complète
            return f"{settings.MEDIA_URL}{obj.image}"  # Fallback si request est None
        return None  # Retourne `None` si l'avatar est vide

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'professor']
