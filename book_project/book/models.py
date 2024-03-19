from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# class CustomUser(AbstractUser):
#     pass


# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    page = models.IntegerField()
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return f"Tokens for {self.user.username}"
