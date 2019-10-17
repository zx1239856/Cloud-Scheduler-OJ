from uuid import uuid1
import json
import hashlib
import mock
from django.test import TestCase, Client
from task_manager.models import TaskSettings
from task_manager.views import getUUID
from user_model.models import UserModel, UserType
from api.common import RESPONSE
import monitor.views


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


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MockCoreV1Api:
    class ReturnItems:
        def __init__(self, item_list):
            self.items = item_list

    def __init__(self, _):
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
        return MockCoreV1Api.ReturnItems(item_list)


class TestTaskSettings(TestCase):
    def setUp(self):
        self.client = Client()
        # create 3o objects
        self.item_list = []
        md5 = hashlib.md5()
        md5.update('adminadmin_salt'.encode('utf8'))
        UserModel.objects.create(uuid=str(getUUID()), username='admin', password=md5.hexdigest(),
                                 email='example@example.com', user_type=UserType.ADMIN, salt='admin_salt')
        md5 = hashlib.md5()
        md5.update('useruser_salt'.encode('utf8'))
        UserModel.objects.create(uuid=str(getUUID()), username='user', password=md5.hexdigest(),
                                 email='example@example.com', user_type=UserType.USER, salt='user_salt')
        for i in range(0, 30):
            item = TaskSettings.objects.create(uuid=str(uuid1()), name="task_{}".format(i), concurrency=30 - i,
                                               task_config={"meta": "meta_string_{}".format(i)})
            self.item_list.append(item)

    def testGetPostListInvalidReq(self):
        token = loginTestUser('user')
        response = self.client.get('/pods/?page=invalid_page', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(monitor.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(monitor.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPodList(self):
        token = loginTestUser('user')
        response = self.client.get('/pods/?page=1', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 51)
        self.assertEqual(response['payload']['page_count'], 3)
