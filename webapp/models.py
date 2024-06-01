from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# Create your models here.

class Staff(models.Model):
    name = models.CharField(max_length=50, default="")
    username = models.CharField(max_length=50, unique=True, default="")
    password = models.CharField(max_length=128, null=True, default=None) 

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

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
    
class Session(models.Model):
    parent = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sessions_as_parent')
    course = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    loginTime = models.TimeField(auto_now_add=True)
    logoutTime = models.TimeField(null=True, blank=True)
    consumedTime = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.parent)
    
class Payment(models.Model):
    parent = models.ForeignKey(Student, on_delete=models.CASCADE)
    payment = models.IntegerField()
    time = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.parent}"


