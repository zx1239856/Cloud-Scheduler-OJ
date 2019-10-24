import json
import mock
import task_manager.executor as executor
from task_manager.executor import Singleton, TaskExecutor
from task_manager.models import TaskSettings
from .common import TestCaseWithBasicUser, MockCoreV1Api, MockThread


@Singleton
class SingletonTest:
    def method(self):
        pass


def get_container_config():
    return {
        "image": "nginx:latest",
        "persistent_volume": {
            "name": "ceph-pvc",
            "mount_path": "/var/image/"
        },
        "shell": "/bin/bash",
        "commands": ["echo hello world", "echo $CLOUD_SCHEDULER_USER"],
        "memory_limit": "128M",
        "working_path": "/home/",
        "task_script_path": "scripts/",
        "task_initial_file_path": "initial/",
    }


@mock.patch.object(executor, 'Thread', MockThread)
@mock.patch.object(executor, 'CoreV1Api', MockCoreV1Api)
class TestTaskExecutor(TestCaseWithBasicUser):
    def testConfigChecker(self):
        config_correct = get_container_config()
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct['commands'] = ''
        self.assertEqual(executor.config_checker(config_correct), False)
        config_correct['commands'] = []
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct.pop('persistent_volume')
        self.assertEqual(executor.config_checker(config_correct), False)
        self.assertEqual(executor.config_checker([]), False)

    def testHelpersFunction(self):
        executor.create_namespace()
        executor.create_userspace_pvc()
        self.assertTrue(executor.get_userspace_pvc())

    def testSingleton(self):
        instance = SingletonTest.instance(new=False)
        self.assertFalse(instance)
        instance_a = SingletonTest.instance()
        instance_b = SingletonTest.instance()
        self.assertEqual(instance_a, instance_b)
        err = False
        try:
            SingletonTest.method()
        except Exception:
            err = True
        self.assertTrue(err)
        instance_a.method()

    def testExecutor(self):
        TaskSettings.objects.create(name='task', uuid='my_uuid', description='',
                                    container_config=json.dumps(get_container_config()),
                                    replica=1, max_sharing_users=1, time_limit=0)
        TaskSettings.objects.create(name='task_invalid', uuid='my_uuid_2', description='',
                                    container_config='{}',
                                    replica=1, max_sharing_users=1, time_limit=0)
        TaskSettings.objects.create(name='task_invalid_2', uuid='my_uuid_3', description='',
                                    container_config='bad_json',
                                    replica=1, max_sharing_users=1, time_limit=0)
        TaskExecutor._instance = None
        task = TaskExecutor.instance(new=True, test=True)
        task.start()
        task.dispatch()
