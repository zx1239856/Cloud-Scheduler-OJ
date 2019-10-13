"""
user models
"""

from django.db import models

# Create your models here.

class UserModel(models.Model):
    """user model"""
    username = models.TextField()
    password = models.TextField()
    salt = models.TextField()


class UserStatus(models.Model):
    """user status"""
    username = models.TextField()
    token = models.TextField()
    expire_time = models.IntegerField()
