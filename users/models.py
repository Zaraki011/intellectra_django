from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('prof', 'Professeur'),
        ('etudiant', 'Étudiant'),
    ]
    role = models.CharField(max_length=10, choices=ROLES, default='etudiant')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})" 