import json
import hashlib
import random
from django.test import Client, TestCase
from user_model.models import UserModel, UserType
from task_manager.views import getUUID


def loginTestUser(user):
    client = Client()
    response = client.post('/user/login/', data=json.dumps({
        'username': user,
        'password': user,
    }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['status'] == 200
    return response['payload']['token']


def mockGetK8sClient():
    return 1


class TestCaseWithBasicUser(TestCase):
    def setUp(self):
        self.client = Client()
        # create 3o objects
        self.item_list = []
        md5 = hashlib.md5()
        md5.update('adminadmin_salt'.encode('utf8'))
        self.admin = UserModel.objects.create(uuid=str(getUUID()), username='admin', password=md5.hexdigest(),
                                              email='example@example.com', user_type=UserType.ADMIN, salt='admin_salt')
        md5 = hashlib.md5()
        md5.update('useruser_salt'.encode('utf8'))
        self.user = UserModel.objects.create(uuid=str(getUUID()), username='user', password=md5.hexdigest(),
                                             email='example@example.com', user_type=UserType.USER, salt='user_salt')


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ReturnItemsList:
    def __init__(self, item_list):
        self.items = item_list


class MockThread:
    def __init__(self, target, **_):
        self._target = target

    def start(self):
        pass


class MockCoreV1Api:
    def __init__(self, _):
        self.pod_dict = {}

    def list_namespaced_pod(self, **kwargs):
        label_selector = kwargs['label_selector']
        namespace = kwargs['namespace']
        if label_selector not in self.pod_dict.keys():
            self.pod_dict[label_selector] = 'Pending'
        elif self.pod_dict[label_selector] == 'Pending':
            self.pod_dict[label_selector] = 'Running'
        elif self.pod_dict[label_selector] == 'Running':
            self.pod_dict[label_selector] = 'Succeeded' if random.randint(0, 2) == 0 else 'Failed'
        item_list = [DotDict({
            'status': DotDict({'pod_ip': 'ip', 'phase': self.pod_dict[label_selector]}),
            'metadata': DotDict({
                'namespace': namespace,
                'name': label_selector,
                'creation_timestamp': '000',
                'uid': 'uid_test',
            }),
            'spec': DotDict({'node_name': 'test_node'})
        })]
        return ReturnItemsList(item_list)

    @staticmethod
    def read_namespaced_pod_log(name, namespace, **_):
        return 'Hello world log from pod {} in ns {}'.format(name, namespace)

    @staticmethod
    def delete_namespaced_pod(**_):
        pass

    @staticmethod
    def list_pod_for_all_namespaces(**_):
        item_list = []
        for i in range(0, 51):
            item_list.append(DotDict({
                'status': DotDict({'pod_ip': 'ip_{}'.format(i), 'phase': 'Running'}),
                'metadata':
                    DotDict({
                        'namespace': 'test_ns',
                        'name': 'pod_{}'.format(i),
                        'creation_timestamp': str(i),
                        'uid': 'uid_{}'.format(i),
                    }),
                'spec': DotDict({'node_name': 'test_node'})
            }))
        return ReturnItemsList(item_list)


class MockBatchV1Api:
    def __init__(self, _):
        pass

    @staticmethod
    def delete_namespaced_job(**_):
        pass

    @staticmethod
    def create_namespaced_job(**_):
        pass
