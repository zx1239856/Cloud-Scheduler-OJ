import random
import json
import time
import mock
from kubernetes import client
from kubernetes.client.rest import ApiException
import task_manager.executor as executor
from task_manager.executor import Singleton, TaskExecutor, Task, TASK, RpcService
from task_manager.models import TaskSettings, TaskVNCPod, TaskStorage
from .common import TestCaseWithBasicUser, MockCoreV1Api, MockThread, ReturnItemsList, DotDict, MockBatchV1Api, \
    MockExtensionsV1beta1Api, MockAppsV1Api


@Singleton
class SingletonTest:
    def method(self):
        pass


def mock_stream(_p0, _p1, _p2, **_):
    return 'empty'


class ConcreteMockCoreV1Api(MockCoreV1Api):
    pod_dict = {}

    def __init__(self, _client):
        super().__init__(self)
        self.pod_occupy = {}

    def list_namespaced_pod(self, **kwargs):
        label_selector = kwargs['label_selector']
        namespace = kwargs['namespace']
        if label_selector not in ConcreteMockCoreV1Api.pod_dict.keys():
            ConcreteMockCoreV1Api.pod_dict[label_selector] = 'Pending'
        elif ConcreteMockCoreV1Api.pod_dict[label_selector] == 'Pending':
            ConcreteMockCoreV1Api.pod_dict[label_selector] = 'Running'
        elif ConcreteMockCoreV1Api.pod_dict[label_selector] == 'Running':
            ConcreteMockCoreV1Api.pod_dict[label_selector] = 'Succeeded' if random.randint(0, 2) == 0 else 'Failed'
        if label_selector not in self.pod_occupy.keys():
            self.pod_occupy[label_selector] = 0
        item_list = [DotDict({
            'status': DotDict({'pod_ip': 'ip', 'phase': ConcreteMockCoreV1Api.pod_dict[label_selector]}),
            'metadata': DotDict({
                'namespace': namespace,
                'name': label_selector,
                'labels': {
                    'occupied': str(self.pod_occupy[label_selector])
                },
                'creation_timestamp': '000',
                'uid': 'uid_test',
            }),
            'spec': DotDict({'node_name': 'test_node'})
        })]
        return ReturnItemsList(item_list)

    @staticmethod
    def read_namespaced_pod(name, namespace):
        return DotDict({
            'status': DotDict({'pod_ip': 'ip', 'phase': 'Running'}),
            'metadata': DotDict({
                'namespace': namespace,
                'name': name,
                'labels': {
                    'occupied': '0'
                },
                'creation_timestamp': '000',
                'uid': 'uid_test',
            }),
            'spec': DotDict({'node_name': 'test_node'})
        })

    @staticmethod
    def patch_namespaced_pod(*_, **__):
        pass


class MockCoreV1ApiForTTL(MockCoreV1Api):
    pod_map = {}

    def __init__(self, _client):
        super().__init__(self)

    def read_namespaced_pod(self, name, namespace):
        print(self, namespace)
        for item_list in MockCoreV1ApiForTTL.pod_map.values():
            for item in item_list:
                if item.metadata.name == name:
                    return item
        raise ApiException(status=404)

    def create_namespaced_pod(self, namespace, body):
        print(namespace)
        name = 'task={}'.format(body.metadata.labels['task'])
        print(name)
        if name in MockCoreV1ApiForTTL.pod_map.keys():
            MockCoreV1ApiForTTL.pod_map[name].append(body)
        else:
            MockCoreV1ApiForTTL.pod_map[name] = [body]
        body.status = client.V1PodStatus
        body.status.phase = 'Pending'
        return body

    def list_namespaced_pod(self, namespace, label_selector):
        print(namespace)
        if label_selector not in MockCoreV1ApiForTTL.pod_map.keys():
            return client.V1PodList(items=[])
        else:
            pods = client.V1PodList(items=MockCoreV1ApiForTTL.pod_map[label_selector].copy())
            if pods.items:
                pods.items[0].status.container_statuses = [
                    client.V1ContainerStatus(state=client.V1ContainerStateTerminated(exit_code=0),
                                             image='aaa', image_id='aaa', name='name', container_id='id',
                                             ready=True, restart_count=0)]
            print("Sending {} pods".format(len(pods.items)))
            return pods

    def delete_namespaced_pod(self, name, namespace):
        print(namespace)
        for item_list in MockCoreV1ApiForTTL.pod_map.values():
            for item in item_list:
                if item.metadata.name == name:
                    item_list.remove(item)
                    break
            print("Remaining: {}".format(len(item_list)))

    def patch_namespaced_pod(self, name, namespace, body):
        print(self, name, namespace, body.metadata.name)


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


class MockThreadedServer:
    def __init__(self, *_, **__):
        pass

    def start(self):
        pass


@mock.patch.object(executor, 'Thread', MockThread)
@mock.patch.object(executor, 'CoreV1Api', ConcreteMockCoreV1Api)
@mock.patch.object(executor, 'BatchV1Api', MockBatchV1Api)
@mock.patch.object(executor, 'ExtensionsV1beta1Api', MockExtensionsV1beta1Api)
@mock.patch.object(executor, 'AppsV1Api', MockAppsV1Api)
@mock.patch.object(executor, 'stream', mock_stream)
@mock.patch.object(executor, 'ThreadedServer', MockThreadedServer)
class TestTaskExecutor(TestCaseWithBasicUser):
    def test_config_checker(self):
        config_correct = get_container_config()
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct['commands'] = ''
        self.assertEqual(executor.config_checker(config_correct), False)
        config_correct['commands'] = []
        self.assertEqual(executor.config_checker(config_correct), True)
        config_correct.pop('persistent_volume')
        self.assertEqual(executor.config_checker(config_correct), False)
        self.assertEqual(executor.config_checker([]), False)

    def test_helpers_function(self):
        executor.create_namespace()
        executor.create_userspace_pvc()
        self.assertTrue(executor.get_userspace_pvc())

    def test_singleton(self):
        instance = SingletonTest.instance(new=False)
        self.assertFalse(instance)
        instance_a = SingletonTest.instance()
        instance_b = SingletonTest.instance()
        self.assertEqual(instance_a, instance_b)
        err = False
        try:
            _ = SingletonTest()
            _.method()
        except Exception as ex:
            print(ex)
            err = True
        self.assertTrue(err)
        instance_a.method()

    def test_rpc_service_handler(self):
        service = RpcService()
        ret = service.exposed_get_user_space_pod('not_exist', 'not_exist')
        self.assertFalse(ret)
        TaskExecutor._instance = None
        TaskExecutor.instance(new=True, test=True)
        ret = service.exposed_get_user_space_pod('test', self.admin.uuid)
        self.assertFalse(ret)

    def test_executor(self):
        settings_correct = TaskSettings.objects.create(name='task', uuid='my_uuid', description='',
                                                       container_config=json.dumps(get_container_config()),
                                                       replica=1, max_sharing_users=1, time_limit=0)
        settings_wrong = TaskSettings.objects.create(name='task_invalid', uuid='my_uuid_2', description='',
                                                     container_config='{}',
                                                     replica=1, max_sharing_users=1, time_limit=0)
        TaskSettings.objects.create(name='task_invalid_2', uuid='my_uuid_3', description='',
                                    container_config='bad_json',
                                    replica=1, max_sharing_users=1, time_limit=0)
        Task.objects.create(settings=settings_correct, user=self.admin, uuid='task', status=TASK.SCHEDULED,
                            logs='')
        Task.objects.create(settings=settings_wrong, user=self.admin, uuid='task_err', status=TASK.SCHEDULED,
                            logs='')
        TaskExecutor._instance = None
        task = TaskExecutor.instance(new=True, test=True)
        task.start()
        task.dispatch()
        task._ttl_check('my_uuid')

        task._job_dispatch()
        item = Task.objects.get(uuid='task')
        item_err = Task.objects.get(uuid='task_err')
        self.assertEqual(item.status, TASK.WAITING)
        self.assertEqual(item_err.status, TASK.FAILED)

        task._job_monitor()
        item = Task.objects.get(uuid='task')
        self.assertEqual(item.status, TASK.PENDING)
        task._job_monitor()
        item = Task.objects.get(uuid='task')
        self.assertEqual(item.status, TASK.RUNNING)
        task._job_monitor()
        item = Task.objects.get(uuid='task')
        self.assertTrue(item.status in (TASK.SUCCEEDED, TASK.FAILED))

        TaskStorage.objects.create(settings=settings_correct, user=self.admin, pod_name='magic_pod',
                                   expire_time=round(time.time()) - 100)
        TaskVNCPod.objects.create(settings=settings_correct, user=self.admin, pod_name='magic_pod',
                                  expire_time=round(time.time() - 100))
        task._storage_pod_monitor()
        task_storage = TaskStorage.objects.get(user=self.admin, settings=settings_correct)
        self.assertEqual(task_storage.pod_name, '')
        self.assertEqual(task_storage.expire_time, 0)

        task.get_user_space_pod('my_uuid', self.admin)

    def test_get_user_vnc_pod(self):
        TaskSettings.objects.create(name='task_okay', uuid='my_uuid_okay', description='',
                                    container_config=json.dumps(get_container_config()),
                                    replica=1, max_sharing_users=1, time_limit=0)
        task = TaskExecutor.instance(new=True, test=True)
        res = task.get_user_vnc_pod('my_uuid_okay', self.admin)
        res2 = task.get_user_vnc_pod('my_uuid_okay', self.admin)
        self.assertEqual(res, res2)


@mock.patch.object(executor, 'stream', mock_stream)
@mock.patch.object(executor, 'CoreV1Api', MockCoreV1ApiForTTL)
class TestTtlCheck(TestCaseWithBasicUser):
    def test_get_user_space_pod_avoid_deleting(self):
        corr = TaskSettings.objects.create(name='task', uuid='my_uuid', description='',
                                           container_config=json.dumps(get_container_config()),
                                           replica=2, max_sharing_users=2, time_limit=0)
        task = TaskExecutor.instance(new=True, test=True)
        TaskStorage.objects.create(user=self.admin, settings=corr, pod_name='my_uuid',
                                   expire_time=round(time.time() + 100000))
        ret = task.get_user_space_pod(corr.uuid, self.admin)  # should never get available pod
        self.assertFalse(ret)
        task._ttl_check(corr.uuid)  # should have 2 available pods
        for item in MockCoreV1ApiForTTL.pod_map['task=my_uuid']:
            item.status.phase = 'Running'  # make'em running
        ret = task.get_user_space_pod(corr.uuid, self.admin)
        self.assertTrue(ret)
        for item in MockCoreV1ApiForTTL.pod_map['task=my_uuid']:
            if item.metadata.name == ret.metadata.name:
                self.assertEqual(ret.metadata.labels['occupied'], '1')

    def test_ttl_check(self):
        corr = TaskSettings.objects.create(name='task', uuid='my_uuid', description='',
                                           container_config=json.dumps(get_container_config()),
                                           replica=2, max_sharing_users=2, time_limit=0)
        task = TaskExecutor.instance(new=True, test=True)
        task._ttl_check('does-not-exist')  # affect nothing
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 2)
        # maintain curr status
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 2)
        for item in MockCoreV1ApiForTTL.pod_map['task=my_uuid']:
            item.status.phase = 'Failed'
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 0)
        # restore
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 2)
        for item in MockCoreV1ApiForTTL.pod_map['task=my_uuid']:
            item.status.phase = 'Running'
        item_0 = MockCoreV1ApiForTTL.pod_map['task=my_uuid'][0]
        item_1 = MockCoreV1ApiForTTL.pod_map['task=my_uuid'][1]
        item_0.metadata.labels['occupied'] = str(2)
        item_1.metadata.labels['occupied'] = str(1)
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 2)
        item_1.metadata.labels['occupied'] = str(2)

        # all occupied, should expand
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 4)

        # should recycle
        item_1.metadata.labels['occupied'] = str(0)
        MockCoreV1ApiForTTL.pod_map['task=my_uuid'][2].status.phase = 'Running'
        task._ttl_check(corr.uuid)
        self.assertEqual(len(MockCoreV1ApiForTTL.pod_map['task=my_uuid']), 3)
