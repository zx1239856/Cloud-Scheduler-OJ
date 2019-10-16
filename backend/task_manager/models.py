"""Models for TaskManager"""
from django.db import models
from user_model import models as user_models


class TASK:
    """TASK Status"""
    SCHEDULED = 0  # waiting to get a pod
    RUNNING = 1  # pod created and running
    SUCCEEDED = 2
    FAILED = 3
    DELETING = 4  # waiting to delete the pod
    PENDING = 5  # waiting the pod initializing


class TaskSettings(models.Model):
    """Task Settings"""
    uuid = models.CharField(max_length=50, unique=True, db_index=True)
    # fetch runner pod according to uuid
    name = models.CharField(max_length=255, unique=True, db_index=True)
    concurrency = models.PositiveIntegerField(default=1)
    # task concurrency, such as image name, scripts, etc.
    task_config = models.TextField()  # stores detailed JSON
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)


class Task(models.Model):
    """Tasks"""
    uuid = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(user_models.UserModel, on_delete=models.CASCADE)
    settings = models.ForeignKey(TaskSettings, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(default=TASK.SCHEDULED)
    create_time = models.DateTimeField(auto_now_add=True)
