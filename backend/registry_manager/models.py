from django.db import models

class ImageStatusCode:
    PENDING = 0
    CACHING = 1
    CACHED = 2
    UPLOADING = 3
    SUCCEEDED = 4
    FAILED = 5


class ImageModel(models.Model):
    """file model"""
    hashid = models.CharField(max_length=255, db_index=True, unique=True, default="null")
    filename = models.CharField(max_length=255, default="null")
    status = models.PositiveSmallIntegerField(default=ImageStatusCode.PENDING)
    uploadtime = models.CharField(max_length=255, default="null")
