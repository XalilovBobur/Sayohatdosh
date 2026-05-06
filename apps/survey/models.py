from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Interest(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.display_name or self.name

class Companion(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class HealthCondition(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Interest)
    companion = models.ForeignKey(Companion, on_delete=models.SET_NULL, null=True)
    health = models.ManyToManyField(HealthCondition, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)  # default qo'shildi
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"