from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Staff(models.Model):
    username = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50, default="")

   