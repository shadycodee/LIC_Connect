from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Staff(models.Model):
    name = models.CharField(max_length=50, default="")
    username = models.CharField(max_length=50, default="")
    password = models.CharField(max_length=128, null=True, default=None) 

    def __str__(self):
        return f"{self.name} {self.username}"
    

class Student(models.Model):
    studentID = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    time_left = models.IntegerField(default=600)

    def __str__(self):
        return self.name