from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='courses/') #hna fin kaystocker les fichiers
    image = models.ImageField(upload_to='images/', null=True, blank=True) #hna fin kaystocker les images
    file_type = models.CharField(max_length=255, choices=[('pdf', 'PDF'), ('video', 'Video')])
    duration = models.CharField(max_length=10)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title