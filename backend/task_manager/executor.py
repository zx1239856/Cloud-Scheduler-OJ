"""
Task executor
"""
import time
import logging
import json
from threading import Thread
from django.db.models import Q
from django.db.utils import OperationalError
from kubernetes import client
from kubernetes.client import BatchV1Api, CoreV1Api
from kubernetes.client.rest import ApiException
from api.common import getKubernetesAPIClient
from config import KUBERNETES_NAMESPACE
from .models import Task, TASK

LOGGER = logging.getLogger(__name__)


def config_checker(json_config):
    if 'image' not in json_config.keys():
        return False
    elif 'persistent_volume' not in json_config.keys():
        return False
    elif 'name' not in json_config['persistent_volume'].keys():
        return False
    elif 'mount_path' not in json_config['persistent_volume'].keys():
        return False
    else:
        return True


class TaskExecutor:
    def __init__(self):
        self.worker_fire_task = Thread(target=self.fire_task)
        self.worker_stop_task = Thread(target=self.stop_task)
        self.worker_monitor_task = Thread(target=self.monitor_task)
        LOGGER.info("Task executor initialized.")

    def start(self):
        self.worker_fire_task.start()
        self.worker_stop_task.start()
        self.worker_monitor_task.start()
        LOGGER.info("Task executor started.")

    @staticmethod
    def monitor_task():
        try:
            api = CoreV1Api(getKubernetesAPIClient())
            while True:
                has_item = False
                for item in Task.objects.filter(Q(status=TASK.RUNNING) | Q(status=TASK.PENDING)).order_by("create_time"):
                    has_item = True
                    common_name = "task-{}".format(item.uuid)
                    try:
                        response = api.list_namespaced_pod(namespace=KUBERNETES_NAMESPACE,
                                                           label_selector="app={}".format(common_name))
                        if response.items:
                            status = response.items[0].status.phase
                            new_status = item.status
                            if status == 'Running':
                                new_status = TASK.RUNNING
                            elif status == 'Succeed':
                                new_status = TASK.SUCCEEDED
                            elif status == 'Pending':
                                new_status = TASK.PENDING
                            elif status == 'Failed':
                                new_status = TASK.FAILED
                            if new_status != item.status:
                                item.status = new_status
                                item.save(force_update=True)
                    except ApiException as ex:
                        LOGGER.warning(ex)
                time.sleep(1 if not has_item else 0.01)
        except OperationalError:
            pass

    @staticmethod
    def fire_task():
        try:
            api = BatchV1Api(getKubernetesAPIClient())
            while True:
                fired = False
                for item in Task.objects.filter(status=TASK.SCHEDULED).order_by("create_time"):
                    running_count = Task.objects.filter(settings=item.settings, status=TASK.RUNNING).count()
                    # 0 for no limit
                    if item.settings.concurrency == 0 or running_count < item.settings.concurrency:
                        # fire task
                        conf = item.settings.task_config.replace("'", "\"")
                        conf = json.loads(conf)
                        common_name = "task-{}".format(item.uuid)
                        storage_name = "shared-{}".format(item.uuid)
                        try:
                            if not config_checker(conf):
                                raise ValueError("Invalid config for TaskSettings: {}".format(item.settings.uuid))
                            # kubernetes part
                            volume_mount = client.V1VolumeMount(mount_path=conf['persistent_volume']['mount_path'],
                                                                name=storage_name)
                            env_username = client.V1EnvVar(name="CLOUD_SCHEDULER_USER", value=item.user.username)
                            env_user_uuid = client.V1EnvVar(name="CLOUD_SCHEDULER_USER_UUID", value=item.user.uuid)
                            container = client.V1Container(name='task-container',
                                                           image=conf['image'],
                                                           volume_mounts=[volume_mount],
                                                           env=[env_username, env_user_uuid])
                            persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
                                claim_name=conf['persistent_volume']['name'],
                                read_only=True
                            )
                            volume = client.V1Volume(name=storage_name,
                                                     persistent_volume_claim=persistent_volume_claim)
                            template = client.V1PodTemplateSpec(
                                metadata=client.V1ObjectMeta(labels={"app": common_name}),
                                spec=client.V1PodSpec(restart_policy="Never",
                                                      containers=[container],
                                                      volumes=[volume]))
                            spec = client.V1JobSpec(template=template, backoff_limit=3)
                            job = client.V1Job(api_version="batch/v1", kind="Job",
                                               metadata=client.V1ObjectMeta(name=common_name),
                                               spec=spec)
                            _ = api.create_namespaced_job(
                                namespace=KUBERNETES_NAMESPACE,
                                body=job
                            )
                            item.status = TASK.PENDING
                            item.save(force_update=True)
                            fired = True
                        except ApiException as ex:
                            LOGGER.warning("Kubernetes ApiException %d: %s", ex.status, ex.reason)
                        except ValueError as ex:
                            LOGGER.warning(ex)
                            item.status = TASK.FAILED
                            item.save(force_update=True)
                        except Exception as ex:
                            LOGGER.error(ex)
                            item.status = TASK.FAILED
                            item.save(force_update=True)
                        break
                if not fired:
                    time.sleep(1)
        except OperationalError:
            pass

    @staticmethod
    def stop_task():
        try:
            api = BatchV1Api(getKubernetesAPIClient())
            while True:
                deleted = False
                for item in Task.objects.filter(status=TASK.DELETING):
                    common_name = "task-{}".format(item.uuid)
                    try:
                        _ = api.delete_namespaced_job(name=common_name,
                                                      namespace=KUBERNETES_NAMESPACE,
                                                      body=client.V1DeleteOptions(
                                                          propagation_policy='Foreground',
                                                          grace_period_seconds=5
                                                      ))
                        deleted = True
                        LOGGER.info("The kubernetes job of Task: %s deleted successfully", item.uuid)
                        item.delete()
                    except ApiException as ex:
                        if ex.status == 404:
                            deleted = True
                            item.delete()
                        else:
                            LOGGER.warning("Kubernetes ApiException %d: %s", ex.status, ex.reason)
                    except Exception as ex:
                        LOGGER.error(ex)
                    break
                if not deleted:
                    time.sleep(1)
        except OperationalError:
            pass
