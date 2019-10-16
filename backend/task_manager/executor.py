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
    try:
        pre_check_fail = ('image' not in json_config.keys() or
                          'persistent_volume' not in json_config.keys() or
                          'name' not in json_config['persistent_volume'].keys() or
                          'mount_path' not in json_config['persistent_volume'].keys())
        if pre_check_fail:
            return False
        elif 'exec' in json_config.keys():
            # check exec part
            return ('shell' in json_config['exec'].keys() and isinstance(json_config['exec']['shell'], str)
                    and 'commands' in json_config['exec'].keys() and isinstance(json_config['exec']['commands'], list))
        else:
            return True
    except Exception as _:
        return False


class TaskExecutor:
    def __init__(self):
        self.worker_fire_task = Thread(target=self.fire_task)
        self.worker_stop_task = Thread(target=self.stop_task)
        self.worker_monitor_task = Thread(target=self.monitor_task)
        self.worker_get_log = Thread(target=self.get_task_log)
        LOGGER.info("Task executor initialized.")

    def start(self):
        self.worker_fire_task.start()
        self.worker_stop_task.start()
        self.worker_monitor_task.start()
        self.worker_get_log.start()
        LOGGER.info("Task executor started.")

    @staticmethod
    def get_task_log():
        try:
            api = CoreV1Api(getKubernetesAPIClient())
            api_batch = BatchV1Api(getKubernetesAPIClient())
            while True:
                for item in Task.objects.filter((Q(status=TASK.SUCCEEDED) | Q(status=TASK.FAILED)) & Q(logs_get=False)):
                    # obtain log
                    try:
                        common_name = "task-{}".format(item.uuid)
                        response = api.list_namespaced_pod(namespace=KUBERNETES_NAMESPACE,
                                                           label_selector="app={}".format(common_name))
                        if response.items:
                            name = response.items[0].metadata.name
                            response = api.read_namespaced_pod_log(name=name,
                                                                   namespace=KUBERNETES_NAMESPACE)
                            if response:
                                item.logs = response
                            item.logs_get = True
                            item.save(force_update=True)
                            # delete this job gracefully
                            try:
                                api_batch.delete_namespaced_job(name=common_name, namespace=KUBERNETES_NAMESPACE)
                            except ApiException as ex:
                                if ex.status != 404:
                                    LOGGER.warning(ex)
                            try:
                                api.delete_namespaced_pod(name=name, namespace=KUBERNETES_NAMESPACE)
                            except ApiException as ex:
                                if ex.status != 404:
                                    LOGGER.warning(ex)
                    except ApiException as ex:
                        LOGGER.warning(ex)
                time.sleep(1)
        except OperationalError:
            pass

    @staticmethod
    def monitor_task():
        try:
            api = CoreV1Api(getKubernetesAPIClient())
            while True:
                for item in Task.objects.filter(Q(status=TASK.RUNNING) | Q(status=TASK.PENDING)).order_by(
                        "create_time"):
                    common_name = "task-{}".format(item.uuid)
                    try:
                        response = api.list_namespaced_pod(namespace=KUBERNETES_NAMESPACE,
                                                           label_selector="app={}".format(common_name))
                        if response.items:
                            status = response.items[0].status.phase
                            new_status = item.status
                            if status == 'Running':
                                new_status = TASK.RUNNING
                            elif status == 'Succeeded':
                                new_status = TASK.SUCCEEDED
                            elif status == 'Pending':
                                new_status = TASK.PENDING
                            elif status == 'Failed':
                                new_status = TASK.FAILED
                            if new_status != item.status:
                                item.status = new_status
                                item.save(force_update=True)
                        else:
                            item.status = TASK.FAILED
                            item.save(force_update=True)
                    except ApiException as ex:
                        LOGGER.warning(ex)
                time.sleep(1)
        except OperationalError:
            pass

    @staticmethod
    def fire_task():
        try:
            api = BatchV1Api(getKubernetesAPIClient())
            while True:
                for item in Task.objects.filter(status=TASK.SCHEDULED).order_by("create_time"):
                    running_count = Task.objects.filter(Q(settings=item.settings) &
                                                        (Q(status=TASK.PENDING) | Q(status=TASK.RUNNING))).count()
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
                            exe = conf.get('exec', {})
                            volume_mount = client.V1VolumeMount(mount_path=conf['persistent_volume']['mount_path'],
                                                                name=storage_name)
                            env_username = client.V1EnvVar(name="CLOUD_SCHEDULER_USER", value=item.user.username)
                            env_user_uuid = client.V1EnvVar(name="CLOUD_SCHEDULER_USER_UUID", value=item.user.uuid)
                            container = client.V1Container(name='task-container',
                                                           image=conf['image'],
                                                           volume_mounts=[volume_mount],
                                                           env=[env_username, env_user_uuid]) if not exe \
                                else client.V1Container(name='task-container', image=conf['image'],
                                                        volume_mounts=[volume_mount],
                                                        env=[env_username, env_user_uuid],
                                                        command=[exe['shell'], '-c'],
                                                        args=[';'.join(exe['commands'])])
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
                time.sleep(1)
        except OperationalError:
            pass

    @staticmethod
    def stop_task():
        try:
            api = BatchV1Api(getKubernetesAPIClient())
            while True:
                for item in Task.objects.filter(status=TASK.DELETING):
                    common_name = "task-{}".format(item.uuid)
                    try:
                        _ = api.delete_namespaced_job(name=common_name,
                                                      namespace=KUBERNETES_NAMESPACE,
                                                      body=client.V1DeleteOptions(
                                                          propagation_policy='Foreground',
                                                          grace_period_seconds=5
                                                      ))
                        LOGGER.info("The kubernetes job of Task: %s deleted successfully", item.uuid)
                        item.delete()
                    except ApiException as ex:
                        if ex.status == 404:
                            item.delete()
                        else:
                            LOGGER.warning("Kubernetes ApiException %d: %s", ex.status, ex.reason)
                    except Exception as ex:
                        LOGGER.error(ex)
                time.sleep(1)
        except OperationalError:
            pass
