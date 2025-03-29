from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if obj.avatar:  
            request = self.context.get('request', None)  # Vérifie si request est présent
            if request is not None:  
                return request.build_absolute_uri(obj.avatar.url)  # Génère une URL complète
            return f"{settings.MEDIA_URL}{obj.avatar}"  # Fallback si request est None
        return None  # Retourne `None` si l'avatar est vide

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'avatar']
