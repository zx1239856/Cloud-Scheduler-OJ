from django.test import TestCase
import task_manager.executor as executor


class TestTaskExecutor(TestCase):
    def testConfigChecker(self):
        config_correct = {
            'name': 'task_test',
            'image': 'image',
            'persistent_volume': {
                'name': 'pvc',
                'mount_path': '/var/mount/'
            },
            'exec': {
                'shell': '/bin/sh',
                'commands': ['echo hello', 'echo hello2']
            }
        }
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct['exec']['shell'] = []
        self.assertEqual(executor.config_checker(config_correct), False)
        config_correct.pop('exec')
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct.pop('persistent_volume')
        self.assertEqual(executor.config_checker(config_correct), False)
        self.assertEqual(executor.config_checker([]), False)
