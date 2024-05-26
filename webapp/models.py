from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Staff(models.Model):
    name = models.CharField(max_length=50, default="")
    username = models.CharField(max_length=50, default="")
    password = models.CharField(max_length=128, null=True, default=None) 

    def __str__(self):
        return f"{self.name} {self.username}"