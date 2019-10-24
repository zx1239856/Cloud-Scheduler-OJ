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
    TLE = 6  # time limit exceeded
    WAITING = 7  # waiting for pod to be created


class TaskSettings(models.Model):
    """Task Settings"""
    uuid = models.CharField(max_length=50, unique=True, db_index=True)
    # fetch runner pod according to uuid
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(max_length=1024)
    # container config, including image, pvc, shell, commands, working_dir, memory limit
    container_config = models.TextField()
    time_limit = models.PositiveIntegerField(default=0)
    replica = models.PositiveIntegerField(default=1)
    ttl_interval = models.PositiveIntegerField(default=2)
    max_sharing_users = models.PositiveIntegerField(default=1)
    # meta data
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)


class Task(models.Model):
    """Tasks"""
    uuid = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(user_models.UserModel, on_delete=models.PROTECT)
    settings = models.ForeignKey(TaskSettings, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(default=TASK.SCHEDULED)
    create_time = models.DateTimeField(auto_now_add=True)
    logs = models.TextField()
    logs_get = models.BooleanField(default=False)


class TaskStorage(models.Model):
    user = models.ForeignKey(user_models.UserModel, on_delete=models.PROTECT, db_index=True)
    settings = models.ForeignKey(TaskSettings, on_delete=models.PROTECT, db_index=True)
    pod_name = models.CharField(max_length=255)
    expire_time = models.PositiveIntegerField(default=0, db_index=True)
