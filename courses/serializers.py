from rest_framework import serializers
from .models import Course, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    professor = serializers.CharField(source='professor.get_full_name', read_only=True)
    category = serializers.CharField(source='category.categoryName', read_only=True)
    file = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    

    def get_file(self, obj):
        if obj.file:  
            request = self.context.get('request', None)  # Vérifie si request est présent
            if request is not None:  
                return request.build_absolute_uri(obj.file.url)  # Génère une URL complète
            return f"{settings.MEDIA_URL}{obj.file}"  # Fallback si request est None
        return None  # Retourne `None` si l'avatar est vide

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
