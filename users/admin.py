from django.contrib import admin
from .models import Utilisateur

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'avatar')  # Affiche les avatars

admin.site.register(Utilisateur, UtilisateurAdmin)
