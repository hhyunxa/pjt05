from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=20, blank=True)
    interest_stocks = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)

# Create your models here.
