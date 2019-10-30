"""
user models
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class UserType:
    ADMIN = 1
    USER = 0


class UserModel(AbstractBaseUser):
    """user model"""
    uuid = models.CharField(max_length=50, db_index=True, unique=True)
    username = models.CharField(max_length=255, db_index=True, unique=True)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)
    user_type = models.PositiveSmallIntegerField(default=UserType.USER)
    email = models.EmailField()
    create_time = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=255, db_index=True, default='')
    token_expire_time = models.IntegerField(default=0)
    REQUIRED_FIELDS = ['email', 'user_type', 'salt', 'uuid']
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
