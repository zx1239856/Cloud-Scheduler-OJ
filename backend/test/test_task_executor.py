from django.test import TestCase
import task_manager.executor as executor


class TestTaskExecutor(TestCase):
    def testConfigChecker(self):
        config_correct = {
            "image": "nginx:latest",
            "persistent_volume": {
                "name": "ceph-pvc",
                "mount_path": "/var/image/"
            },
            "shell": "/bin/bash",
            "commands": ["echo hello world", "echo $CLOUD_SCHEDULER_USER"],
            "memory_limit": "128M",
            "working_path": "/home/"
        }
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct['commands'] = ''
        self.assertEqual(executor.config_checker(config_correct), False)
        config_correct['commands'] = []
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct.pop('persistent_volume')
        self.assertEqual(executor.config_checker(config_correct), False)
        self.assertEqual(executor.config_checker([]), False)
