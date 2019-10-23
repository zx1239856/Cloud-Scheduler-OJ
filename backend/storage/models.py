from django.db import models

class FileStatusCode:
    PENDING = 0
    CACHING = 1
    CACHED = 2
    UPLOADING = 3
    SUCCEEDED = 4
    FAILED = 5

class FileModel(models.Model):
    """file model"""
    hashid = models.CharField(max_length=255, db_index=True, unique=True, default="null")
    filename = models.CharField(max_length=255, default="null")
    targetpvc = models.CharField(max_length=255, default="null")
    targetpath = models.CharField(max_length=255, default="null")
    status = models.PositiveSmallIntegerField(default=FileStatusCode.PENDING)
    uploadtime = models.CharField(max_length=255, default="null")
